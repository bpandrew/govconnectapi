import requests
import json
import pandas as pd
import numpy as np
from pandas.io.json import json_normalize
from datetime import datetime, date, time, timedelta

import hashlib, binascii, os
import humanize
from flask import Flask, request, jsonify, session, redirect, url_for, g, Response

def opportunity(data, agency_id, category_dict):

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
	df["contract_ongoing"] = df["dt_contract_end"] > datetime.now() # Is the contract still open?
	df["contract_ending_soon"] = df["dt_contract_end"] < datetime.now()+timedelta(days=30) # Is the contract still open?

	# get the number of years back 
	df['current_fy'] = datetime.now()
	df['current_fy'] = pd.to_datetime(df.current_fy).dt.to_period('A-JUN')
	df['current_fy'] = df['current_fy'].map(lambda x: x.year).astype(int)
	df['years_back'] = df['current_fy'].astype(int)-df['financial_year'].astype(int)

	# Fill all of the gaps in the data
	df = df.fillna("")

	# Filter teh DF by agency and category
	df_op = df.copy()
	df_op['count']=1

	#print(df)

	agency_id = 10 # *************    TEMPORARY  ****************

	contract_data = {}

	#df_op = df_op[df_op['agency.id']==agency_id]
	
	for category in category_dict:

		print(category)
			
		#df_op = df_op[df_op['unspsc.id']==category['data']['id']]
		print(category['ids'])
		print(category['data']['id'])
		df_op = df_op[df_op['unspsc.id'].isin(category['ids'])]
		
		contract_data[category['level']] = {"unspsc":category['data'], "contracts":[], "ids":category['ids'] }

		if len(df_op)>0:
		
			# Save ALL of the contracts to JSON
			for index, row in df_op.iterrows():
				temp_data = {"unspsc_id":row['unspsc.id'],  "id":row['id'], "contract_ending_soon":row['contract_ending_soon'], "agency":row['agency.display_title'], "agency_id":row['agency.id'], "branch":row['branch.display_title'], "division":row['division.display_title'], "contract_end":row['contract_end'], "contract_start":row['contract_start'], "contract_value":row['contract_value'], "supplier_name":row['supplier.name'], "supplier_id":row['supplier.id'], "title":row['title'], "contract_ongoing":row['contract_ongoing'], "years_back":row['years_back'], "financial_year":row['financial_year']}
				contract_data[category['level']]['contracts'].append(temp_data) 
				

			contract_data[category['level']]['agency_id'] = agency_id
			contract_data[category['level']]['category_id'] = category['data']['id']

			# Number of contracts in the df
			contract_data[category['level']]['no_contracts'] = df_op['id'].count()

			# Average value of contracts
			contract_data[category['level']]['avg_value'] = int(df_op['contract_value'].mean())

			# number of suppliers
			contract_data[category['level']]['no_suppliers'] = df_op['supplier.id'].nunique()

			# Contracts awarded per month
			month_count = df_op['month'].value_counts() # number of records/contracts per month in this df
			try:
				contract_data[category['level']]['avg_contracts_month'] = int(sum(month_count) / len(month_count))
			except:
				contract_data[category['level']]['avg_contracts_month'] = "N/A"
			contract_data[category['level']]['contracts_month'] = month_count.to_dict()

			# Get the earnings per supplier
			contract_data[category['level']]['supplier_data'] = []

			df_temp = df_op.groupby(['supplier.display_name']).sum().reset_index()
			df_temp = df_temp.sort_values(by='contract_value', ascending=0)
			for index, row in df_temp.iterrows():
				temp_data = {"earnings":row['contract_value'], "no_contracts":row['count'], "name":row['supplier.display_name'], "avg_duration":row['contract_duration']/row['count'], "avg_value":row['contract_value']/row['count']}
				contract_data[category['level']]['supplier_data'].append(temp_data) 

			no_contracts = df_temp['count'].sum()
			total_value = df_temp['contract_value'].sum()

			df_top10 = df_temp[:10].copy()
			contract_data[category['level']]['supplier_pie_chart'] = []
			print(df_top10)
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


		
	return contract_data 
