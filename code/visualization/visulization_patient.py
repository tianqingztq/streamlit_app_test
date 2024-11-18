import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from collections import defaultdict
import matplotlib.pyplot as plt


# FHIR Server
FHIR_SERVER_URL = "http://18.222.194.135:3838/fhir"

def fetch_all_patients():
    patients = []
    url = f"{FHIR_SERVER_URL}/Patient?_count=100"

    while url:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if 'entry' in data:
            patients.extend(data['entry'])

        url = next((link['url'] for link in data.get('link', []) if link['relation'] == 'next'), None)

    return pd.json_normalize(patients)

def fetch_all_observations():
    observations = []
    url = f"{FHIR_SERVER_URL}/Observation?_count=100"

    while url:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if 'entry' in data:
            observations.extend(data['entry'])

        url = next((link['url'] for link in data.get('link', []) if link['relation'] == 'next'), None)

    return pd.json_normalize(observations)




def run_patient_visulization():
    # Fetch data
    patient_data = fetch_all_patients()
    observations_data = fetch_all_observations()

    if not patient_data.empty and not observations_data.empty:
        # Extract Patient ID from observations
        observations_data['patient_id'] = observations_data['resource.subject.reference'].str.split('/').str[1]
        
        # Initialize an empty DataFrame for visualization without predefining columns
        visulization_df = pd.DataFrame()
        
        for id in patient_data['resource.id']:
            
            # Create a temporary DataFrame for the current patient_id
            temp_df = pd.DataFrame({'patient_id': [id]})
            
            # Get the dignostics values for the current patient_id
            diagnostic_values = observations_data[observations_data['patient_id'] == id]['resource.code.coding'].apply(
                lambda x: [item['display'] for item in x] if isinstance(x, list) else []
            )
        
            
            # Add three diag into visualization table
            if len(diagnostic_values.tolist()) == 0:
                temp_df['obs_diag_1'] = 'Unknown'
                temp_df['obs_diag_2'] = 'Unknown'
                temp_df['obs_diag_3'] = 'Unknown'
                temp_df['obs_diag_4'] = 'Unknown'
                temp_df['obs_diag_5'] = 'Unknown'
                temp_df['obs_diag_6'] = 'Unknown'
            elif len(diagnostic_values.tolist()) == 1:
                temp_df['obs_diag_1'] = diagnostic_values.tolist()[0]
                temp_df['obs_diag_2'] = 'Unknown'
                temp_df['obs_diag_3'] = 'Unknown'
                temp_df['obs_diag_4'] = 'Unknown'
                temp_df['obs_diag_5'] = 'Unknown'
                temp_df['obs_diag_6'] = 'Unknown'
            elif len(diagnostic_values.tolist()) == 2:
                temp_df['obs_diag_1'] = diagnostic_values.tolist()[0]
                temp_df['obs_diag_2'] = diagnostic_values.tolist()[1]
                temp_df['obs_diag_3'] = 'Unknown'
                temp_df['obs_diag_4'] = 'Unknown'
                temp_df['obs_diag_5'] = 'Unknown'
                temp_df['obs_diag_6'] = 'Unknown'
            elif len(diagnostic_values.tolist()) == 3:
                temp_df['obs_diag_1'] = diagnostic_values.tolist()[0]
                temp_df['obs_diag_2'] = diagnostic_values.tolist()[1]
                temp_df['obs_diag_3'] = diagnostic_values.tolist()[2]
                temp_df['obs_diag_4'] = 'Unknown'
                temp_df['obs_diag_5'] = 'Unknown'
                temp_df['obs_diag_6'] = 'Unknown'
            elif len(diagnostic_values.tolist()) == 4:
                temp_df['obs_diag_1'] = diagnostic_values.tolist()[0]
                temp_df['obs_diag_2'] = diagnostic_values.tolist()[1]
                temp_df['obs_diag_3'] = diagnostic_values.tolist()[2]
                temp_df['obs_diag_4'] = diagnostic_values.tolist()[3]
                temp_df['obs_diag_5'] = 'Unknown'
                temp_df['obs_diag_6'] = 'Unknown'
            elif len(diagnostic_values.tolist()) == 5:
                temp_df['obs_diag_1'] = diagnostic_values.tolist()[0]
                temp_df['obs_diag_2'] = diagnostic_values.tolist()[1]
                temp_df['obs_diag_3'] = diagnostic_values.tolist()[2]
                temp_df['obs_diag_4'] = diagnostic_values.tolist()[3]
                temp_df['obs_diag_5'] = diagnostic_values.tolist()[4]
                temp_df['obs_diag_6'] = 'Unknown'
            elif len(diagnostic_values.tolist()) == 6:
                temp_df['obs_diag_1'] = diagnostic_values.tolist()[0]
                temp_df['obs_diag_2'] = diagnostic_values.tolist()[1]
                temp_df['obs_diag_3'] = diagnostic_values.tolist()[2]
                temp_df['obs_diag_4'] = diagnostic_values.tolist()[3]
                temp_df['obs_diag_5'] = diagnostic_values.tolist()[4]
                temp_df['obs_diag_6'] = diagnostic_values.tolist()[5]
                
            # Retrieve gender, age, and race from patient_data
            patient_info = patient_data[patient_data['resource.id'] == id]
            if not patient_info.empty:
                temp_df['gender'] = patient_info['resource.gender'].values[0]
                extensions = patient_info['resource.extension'].values[0]
                age = None
                race = None
                
                # Extract age and race from extensions
                for ext in extensions:
                    if ext['url'] == 'age':
                        age = ext['valueString']
                    elif ext['url'] == 'ombCategory':
                        race = ext['valueCoding']['display'] if 'valueCoding' in ext else None
                
                temp_df['age'] = age if age is not None else 'Unknown'
                temp_df['race'] = race if race is not None else 'Unknown'
            else:
                temp_df['gender'] = 'Unknown'
                temp_df['age'] = 'Unknown'
                temp_df['race'] = 'Unknown'
            
            # Extract weight range from observations
            weight_range = None
            patient_observations = observations_data[observations_data['patient_id'] == id]
            if not patient_observations.empty:
                for index, row in patient_observations.iterrows():
                    # Process weight ranges
                    extensions = row.get('resource.extension', [])
                    low_value = None
                    high_value = None
                    if isinstance(extensions, list):  # Check if extensions is a list
                        for ext in extensions:
                            if ext.get('url') == 'http://hl7.org/fhir/StructureDefinition/observation-weight-range':
                                value_quantity = ext.get('valueQuantity', {})
                                if isinstance(value_quantity, dict):
                                    weight_value = value_quantity.get('value', None)
                                    # Check if weight_value is not None and set low_value or high_value accordingly
                                    if weight_value is not None:
                                        if low_value is None:
                                            low_value = weight_value  # Set the first value as low_value
                                        elif high_value is None:
                                            high_value = weight_value  # Set the second value as high_value
                                        # If both values are already set, you can break if you only want the first pair
                                        if low_value is not None and high_value is not None:
                                            break  # Exit loop if both values are found

                    # Set weight_range only if both low_value and high_value are found
                    if low_value is not None and high_value is not None:
                        weight_range = (low_value, high_value)
            if weight_range is not None:
                temp_df['weight_range'] = [weight_range]  # Wrap in a list to match the DataFrame's length
            else:
                temp_df['weight_range'] = ["Unknown"]  # Use a list containing None to maintain length

            
            # Append the temporary DataFrame to the main DataFrame
            visulization_df = pd.concat([visulization_df, temp_df], ignore_index=True)

    # Export to CSV
    # visulization_df.to_csv("visulization.csv", index=False)

    # ---------------------- Visualization -----------------------------
    # Streamlit application configuration
    # st.title("Diabetes Patient Data Visualization For PCP")

    # Add a main section title
    st.header("Patient Information")


    # Filters
    ## TODO

    # Age Pie Chart
    with st.expander("Age", expanded=True):
        age_counts = visulization_df['age'].value_counts().reset_index()
        age_counts.columns = ['Age', 'Count']
        fig = px.pie(age_counts, values='Count', names='Age', title='Age Distribution')
        st.plotly_chart(fig)

    # Gender Pie Chart
    with st.expander("Gender", expanded=True):
        gender_counts = visulization_df['gender'].value_counts().reset_index()
        gender_counts.columns = ['Gender', 'Count']
        fig = px.pie(gender_counts, values='Count', names='Gender', title='Gender Distribution')
        st.plotly_chart(fig)

    # Race Pie Chart
    with st.expander("Race", expanded=True):
        race_counts = visulization_df['race'].value_counts().reset_index()
        race_counts.columns = ['Race', 'Count']
        fig = px.pie(race_counts, values='Count', names='Race', title='Race Distribution')
        st.plotly_chart(fig)

    # Weight Histogram
    with st.expander("Weight", expanded=True):
        # Count occurrences of each weight range, including 'Unknown'
        weight_counts = visulization_df['weight_range'].value_counts().reset_index()
        weight_counts.columns = ['weight_range', 'count']

        # Ensure the weight_range is of string type for plotting
        weight_counts['weight_range'] = weight_counts['weight_range'].astype(str)

        # Create the bar chart for weight distribution
        fig = px.bar(weight_counts, x='weight_range', y='count', 
                    color='count', title='Weight Range Distribution (kg)',
                    labels={'weight_range': 'Weight Range (kg)', 'count': 'Count'},
                    color_continuous_scale=px.colors.sequential.Blues)

        # Show the plot
        st.plotly_chart(fig)

        # Additional note below the weight histogram
        st.markdown("**Note:** Weight is represented in kilograms (kg).")
