from flask import Flask, request, jsonify, render_template, session, redirect, url_for, g, Response
import json
from datetime import datetime, date, time, timedelta
import humanize
import random, string
import pandas as pd
import numpy as np

# Bhuilds the chart data using dataframes for the current and previous financial year
def chart_revenue(df, lfy_start, lfy_end, cfy_start, cfy_end):
    # find the daily value for all of the contracts the supplier has
    date_list = []
    value_list = []

    #generate place holder zero values in each day.
    fy_start = datetime.strptime(lfy_start, '%Y-%m-%d')
    for x in range(730): # two years
        insert_date = fy_start + timedelta(days=x)
        date_list.append(insert_date)
        value_list.append(0)
        
    # Loop over each of the rows in the dataframe
    for index, row in df.iterrows():

        contract_duration = row['contract_duration']
        contract_value = row['contract_value']
        daily_rate = contract_value/contract_duration
        start_date = datetime.strptime(row['contract_start'], '%Y-%m-%d')
        
        for i in range(contract_duration):
            insert_date = start_date + timedelta(days=i)
            date_list.append(insert_date)
            value_list.append(daily_rate)


    # Create an empty dataframe
    df_revenue = pd.DataFrame()

    # Create a column from the datetime variable
    df_revenue['datetime'] = date_list
    # Convert that column into a datetime datatype
    df_revenue['datetime'] = pd.to_datetime(df_revenue['datetime'])
    # Set the datetime column as the index
    df_revenue.index = df_revenue['datetime'] 
    # Create a column from the numeric score variable
    df_revenue['value'] = value_list
    
    df_revenue_lfy = df_revenue[df_revenue['datetime']<=lfy_end]
    df_revenue_lfy = df_revenue_lfy[df_revenue_lfy['datetime']>=lfy_start]
    # Group it monthly
    df_monthly_lfy = df_revenue_lfy.resample('M').sum()
    
    df_revenue_cfy = df_revenue[df_revenue['datetime']<=cfy_end]
    df_revenue_cfy = df_revenue_cfy[df_revenue_cfy['datetime']>=cfy_start]
    # Group it monthly
    df_monthly_cfy = df_revenue_cfy.resample('M').sum()
    #return df_monthly_cfy

    # Create the data arrays for the graph
    lfy_graph_x = []
    lfy_graph_y = []
    cfy_graph_x = []
    cfy_graph_y = []
    
    for index, row in df_monthly_lfy.iterrows():
        month = datetime.strptime(str(index)[:10], '%Y-%m-%d')
        lfy_graph_x.append(month.strftime("%B"))
        lfy_graph_y.append(round(row['value'], 2))
        
    for index, row in df_monthly_cfy.iterrows():
        month = datetime.strptime(str(index)[:10], '%Y-%m-%d')
        cfy_graph_x.append(month.strftime("%B"))
        cfy_graph_y.append(round(row['value'], 2))
        
    #print(df_monthly_lfy)
        
    return lfy_graph_x, lfy_graph_y, cfy_graph_x, cfy_graph_y


def chart_agency_revenue(df, lfy_start, lfy_end, cfy_start, cfy_end):
    agency_list = []
    agency_id_list = []
    cfy_values = []
    lfy_values = []
    
    # restrict to the last 2 FYs
    df = df[df['contract_start']>=lfy_start]
    df = df[df['contract_value']>0]
    
    df_temp = df.groupby(['agency.id']).sum().reset_index()
    df_temp = df_temp[df_temp['contract_value']>0]
    df_temp.sort_values(by=['contract_value'], inplace=True, ascending=False)
    # Get all of the agencies for the last 2 years
    agency_id_list = df_temp['agency.id'].tolist()
    
    
    df_temp = df[df['contract_start']<=lfy_end]
    df_temp = df_temp.groupby(['agency.id']).sum().reset_index()
    lfy_agencies = len(df_temp)
    if lfy_agencies==1:
        lfy_agencies = humanize.apnumber(lfy_agencies)+" agency"
    else:
        lfy_agencies = humanize.apnumber(lfy_agencies)+" agencies"
        
    for item in agency_id_list:
        agency_list.append(df[df['agency.id']==item]['agency.title'].values[0])
        try:
            agency_revenue = df_temp[df_temp['agency.id']==item]['contract_value'].values[0]
        except:
            agency_revenue =0
        lfy_values.append(agency_revenue)
        
 
    df_temp = df[df['contract_start']>=cfy_start]
    df_temp = df_temp[df_temp['contract_start']<=cfy_end]
    df_temp = df_temp.groupby(['agency.id']).sum().reset_index()
    cfy_agencies = len(df_temp)
    if cfy_agencies==1:
        cfy_agencies = humanize.apnumber(cfy_agencies)+" agency"
    else:
        cfy_agencies = humanize.apnumber(cfy_agencies)+" agencies"
    for item in agency_id_list:
        try:
            agency_revenue = df_temp[df_temp['agency.id']==item]['contract_value'].values[0]
        except:
            agency_revenue =0
        cfy_values.append(agency_revenue)

    chart_height = (len(agency_list)*40)+100 # 50 pixels per grouped bar chart/agency
        
        
    # Calculate the Growth/Shrinkage for each agency
    #for item in lfy_values:
    #    change = 
        
    return agency_list, lfy_values, cfy_values, chart_height, lfy_agencies, cfy_agencies
    
