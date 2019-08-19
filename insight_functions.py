import requests
import json
import pandas as pd
import numpy as np
from pandas.io.json import json_normalize
from datetime import datetime, date, time, timedelta
import functions
import hashlib, binascii, os
import humanize
from flask import Flask, request, jsonify, session, redirect, url_for, g, Response


def clean_contract_df(data):
	# Save the results to a dataframe
	df = json_normalize(data)
	#df = df.drop(['branch', 'division', 'son', 'unspsc'], axis=1) # drop the json 'column headers'

	# Clean up the dataframe, format the dates, and add in financial year data
	df['dt_publish_date'] = pd.to_datetime(df['publish_date'])
	df['dt_contract_start'] = pd.to_datetime(df['contract_start'])
	df['dt_contract_end'] = pd.to_datetime(df['contract_end'])
	df['month'] = df['dt_contract_start'].map(lambda x: x.month)
	df['calendar_year'] = df['dt_contract_start'].map(lambda x: x.year)

	df['contract_value'] = df['contract_value'].astype(str)
	df = df[~df.contract_value.str.contains("Original")]
	df['contract_value'] = df['contract_value'].astype(float)
	df['financial_year'] = pd.to_datetime(df.dt_contract_start).dt.to_period('A-JUN')
	df['financial_year'] = df['financial_year'].map(lambda x: x.year).astype(int)
	df['calendar_quarter'] = df.dt_contract_start.dt.quarter 
	df['financial_quarter'] = df.dt_contract_start.dt.quarter - 2
	df["contract_ongoing"] = df["dt_contract_end"] > datetime.now() # Is the contract still open?
	df["contract_ending_soon"] = df["dt_contract_end"] < datetime.now()+timedelta(days=30) # Is the contract still open?

	# get the number of years back 
	df['current_fy'] = datetime.now()
	df['current_fy'] = pd.to_datetime(df.current_fy).dt.to_period('A-JUN')
	df['current_fy'] = df['current_fy'].map(lambda x: x.year).astype(int)
	df['years_back'] = df['current_fy'].astype(int)-df['financial_year'].astype(int)

	# Fill all of the gaps in the data
	df = df.fillna("")
	return df




def supplier_agency_segment_matrix(df, supplier_id, unspsc_segments, unspsc_dict, agencies, financial_year, financial_quarter):
	# A matrix for each supplier, showing total revenue by agency (y) and segment (x).

	try:
		# Find the UNSPSC Segment ID and add it to the dataframe
		df['segment_unspsc'] = df.apply(lambda row: row['unspsc.unspsc'][:2], axis=1)
		# Remove the contracts where there is no segment
		df = df[df['segment_unspsc']!=""]
		# Lookup the ID of the segment from the dictionary
		df['segment_unspsc_id'] = df.apply(lambda row: unspsc_dict[row['segment_unspsc']], axis=1)

		# filter the dataframe by financial year and/or financial quarter
		df_temp = df[ (df['financial_year']==financial_year) ]
		if financial_quarter!=0:
			df_temp = df_temp[ (df_temp['financial_quarter']==financial_quarter) ]

		matrixes = [] # holds all of the generated matrixes, so it can be passed back and added to the db
		# Generate the Matrix for the supplier

		df_temp = df_temp[(df_temp['supplier.id']==supplier_id) | (df_temp['supplier.umbrella_id']==supplier_id)]
		df_temp = df_temp.groupby(['agency.id', 'segment_unspsc_id']).sum()
		json_dict = {"supplier_id":supplier_id, "data":{}}
		for index, row in df_temp.iterrows(): 
			json_dict['data']['a_'+str(index[0])]={}
		for index, row in df_temp.iterrows():     
			json_dict['data']['a_'+str(index[0])][index[1]]=row['contract_value']
		json.dumps(json_dict)

		#matrix = matrix_json(supplier_id, df_temp, unspsc_segments, agencies, True)
		matrixes.append({"supplier_id":supplier_id, "data":json.dumps(json_dict)})
		#print(json.dumps(json_dict))

		return matrixes
	except:
		return None



def create_matrix(unspscs, agencies):
	data = {'agency': agencies}

	# create an empty array the same length as the number of agencies
	empty_arr = []
	for i in range(len(data['agency'])):
		empty_arr.append(0)

	# Loop through and create an empty dataframe for agencies vs unspsc
	for item in unspscs:
		data[item] = empty_arr

	df_matrix = pd.DataFrame(data)
	df_matrix['agency'] = "a_"+ df_matrix['agency'].astype(str)
	
	# set the agency as the index column
	df_matrix.set_index('agency', drop=True, append=False, inplace=True, verify_integrity=False)
	#df_matrix
	return df_matrix


def populate_matrix(supplier_id, df, unspscs, agencies):
	# Filter the dataframe
	# Check for all contracts for the supplier, and any companies where the supplier is a child
	df_temp = df[(df['supplier.id']==supplier_id) | (df['supplier.umbrella_id']==supplier_id) ]
	df_temp = df_temp.groupby(['agency.id', 'segment_unspsc_id']).sum()
	df_matrix = create_matrix(unspscs, agencies) # Create the empty matrix
	# populate the matrix
	for index, row in df_temp.iterrows():
		agency = "a_"+ str(index[0])
		unspsc = int(index[1])
		value = row['contract_value']
		df_matrix[unspsc][agency] = value
        
	return df_matrix


def matrix_json(supplier_id, df, unspscs, agencies, compress):
	matrix = populate_matrix(supplier_id, df, unspscs, agencies)
	if compress==True:
		matrix = compress_matrix(matrix) # remove all of the rows and columns with no activity for storage in the db
	json_data = matrix.to_json(orient='index')
	return json_data


def compress_matrix(matrix):
    # gets rid of all of the rows and columns (agencies and categories) where there is no activity.
    matrix = matrix.fillna(0) # remove any NaN values
    matrix = matrix.loc[:, (matrix != 0).any(axis=0)]
    matrix = matrix[(matrix.T != 0).any()]
    return matrix


def rebuild_matrix(json_data, unspscs, agencies):
	# read matrix and reconstitute it from JSON storage
	db_matrix = pd.read_json(json_data, orient='index')
	db_matrix.index = db_matrix.index.astype(str)
	np_matrix = db_matrix.stack()
	dataset = pd.DataFrame(np_matrix)
    
	df_matrix = create_matrix(unspscs, agencies)
    
	for index, row in dataset.iterrows():
		agency = str(index[0])
		unspsc = int(index[1])
		value = row[0]
		df_matrix.loc[agency][unspsc] = value   

	return df_matrix


def calc_competition(matrix_a, matrix_b):
    value_weighting_factor = 3

    agency_sum = np.sum(matrix_a, axis=1)
    total_earnings = np.sum(agency_sum)
    # Generate the matrix holding all the scores
    score_matrix = ((matrix_b-matrix_a)/matrix_a)*((matrix_a/total_earnings)**value_weighting_factor)
    agency_competitiom_sum = np.sum(score_matrix, axis=1)
    competitor_score = np.sum(agency_competitiom_sum)
    return competitor_score




# ------------------------------------------ OPPORTUNITY -------------------------------------------
# --------------------------------------------------------------------------------------------------

def opportunity(data, agency_id, category_dict):

	# Save the results to a dataframe
	df = clean_contract_df(data)

	contract_data = {}

	for category in category_dict:
		df_op = df.copy()
		df_op['count']=1
		i=0
		for i in range(2):

			# If it is the second time through, filter by agency.
			if i>0:
				category['level'] = category['level']+"_filtered"
				df_op = df_op[df_op['agency.id']==agency_id]

			# Filter by UNSPSC
			df_op = df_op[df_op['unspsc.id'].isin(category['ids'])]
			
			contract_data[category['level']] = {"unspsc":category['data'], "contracts":[], "ids":category['ids'] }

			contract_data[category['level']]['supplier_data'] = []
			contract_data[category['level']]['supplier_pie_chart'] = []
			contract_data[category['level']]['agency_id'] = agency_id
			contract_data[category['level']]['category_id'] = category['data']['id']

			if len(df_op)>0:
			
				# Save ALL of the contracts to JSON
				for index, row in df_op.iterrows():
					temp_data = {"unspsc_id":row['unspsc.id'], "id":row['id'], "contract_ending_soon":row['contract_ending_soon'], "agency":row['agency.display_title'], "agency_id":row['agency.id'], "branch":row['branch.display_title'], "division":row['division.display_title'], "contract_end":row['contract_end'], "contract_start":row['contract_start'], "contract_value":functions.format_currency_comma(row['contract_value']), "supplier_name":row['supplier.display_name'], "supplier_id":row['supplier.id'], "title":row['title'], "contract_ongoing":row['contract_ongoing'], "years_back":row['years_back'], "financial_year":row['financial_year']}
					contract_data[category['level']]['contracts'].append(temp_data) 

				# Number of contracts in the df
				contract_data[category['level']]['no_contracts'] = df_op['id'].count()

				# Average value of contracts
				contract_data[category['level']]['avg_value'] = functions.format_currency_comma(int(df_op['contract_value'].mean()), True)

				# number of suppliers
				contract_data[category['level']]['no_suppliers'] = df_op['supplier.id'].nunique()

				# Contracts awarded per month
				month_count = df_op['month'].value_counts() # number of records/contracts per month in this df
				contract_data[category['level']]['avg_contracts_month'] = round(float(sum(month_count) / 12), 1) # len(month_count)
				contract_data[category['level']]['contracts_month'] = month_count.to_dict()

				# Get the earnings per supplier
				
				df_temp = df_op.groupby(['supplier.display_name']).sum().reset_index()
				df_temp = df_temp.sort_values(by='contract_value', ascending=0)
				for index, row in df_temp.iterrows():
					temp_data = {"earnings":row['contract_value'], "no_contracts":row['count'], "name":row['supplier.display_name'], "avg_duration":row['contract_duration']/row['count'], "avg_value":row['contract_value']/row['count']}
					contract_data[category['level']]['supplier_data'].append(temp_data) 

				no_contracts = df_temp['count'].sum()
				total_value = df_temp['contract_value'].sum()

				df_top10 = df_temp[:10].copy()
				
				# Get the top 10 suppliers and format the pie chart data
				for index, row in df_top10.iterrows():
					temp_data = {"earnings":int(row['contract_value']), "no_contracts":row['count'], "name":row['supplier.display_name']}
					contract_data[category['level']]['supplier_pie_chart'].append(temp_data)

				if len(df_temp)>10:
					# Find the remainder of contracts 
					other_contracts = no_contracts - df_top10['count'].sum()
					other_value = total_value - df_top10['contract_value'].sum()
					temp_data = {"earnings":other_value, "no_contracts":other_contracts, "name":"Other"}
					contract_data[category['level']]['supplier_pie_chart'].append(temp_data)

			i=i+1



	

	#df_temp = df_op.groupby(['division.id', 'division.display_title']).mean().reset_index()

	#contract_data['division_contracts'] = []
	#for index, row in df_temp.iterrows():
	#	temp_dict = {"division_title":row['division.display_title'], "avg_contract_value":row['contract_value'], "avg_contract_duration":int(row['contract_duration'])}
	#	contract_data['division_contracts'].append(temp_dict)

	#df_temp = df_op.groupby(['division.id', 'division.display_title']).sum().reset_index()
	#for index, row in df_temp.iterrows():
	#	contract_data['division_contracts'][index]['sum_contracts']=row['contract_value']
	#	contract_data['division_contracts'][index]['contract_count']=row['count']

	# Compare the category contracts, to see if there is a change between general and specific categories
	temp_arr_a = np.asarray(contract_data['family']['contracts'])
	try:
		temp_arr_b = np.asarray(contract_data['class']['contracts'])
	except:
		temp_arr_b = []
	try:
		temp_arr_c = np.asarray(contract_data['commodity']['contracts'])
	except:
		temp_arr_c = []

	# does the family == the class. ie. all contracts  in the class are the same as in the family.
	family_class = np.array_equal(temp_arr_a,temp_arr_b)
	if family_class==True:
		contract_data['family']['category_nochange']=True
	else:
		contract_data['family']['category_nochange']=False

	if len(temp_arr_b)>0:
		class_commodity = np.array_equal(temp_arr_b,temp_arr_c)
		if class_commodity==True:
			contract_data['class']['category_nochange']=True
		else:
			contract_data['class']['category_nochange']=False


	insight_data = {}
	for level in contract_data:
		try:
			#print(level)
			#level = "family"
			# create the JSON data to populate the insight summary
			try:
				insight_top_supplier = contract_data[level]['supplier_data'][0]['name']
			except:
				insight_top_supplier = "N/A"
			insight_data[level] = {"ids": contract_data[level]['ids'], "insight_avg_value": contract_data[level]['avg_value'], "insight_category_name": contract_data[level]['unspsc']['title'], "insight_avg_contract": contract_data[level]['avg_contracts_month'], "insight_no_suppliers": contract_data[level]['no_suppliers'], "insight_top_supplier":insight_top_supplier, "insight_chart_data": contract_data[level]['supplier_pie_chart']}
		except:
			pass

	contract_data['insight_data'] = insight_data
		
	return contract_data 
