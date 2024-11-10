import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from collections import defaultdict
import matplotlib.pyplot as plt


# FHIR Server
FHIR_SERVER_URL = "https://fhir-server-cs6440-final.ngrok.io/fhir/"

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


def fetch_all_medicationrequest():
    observations = []
    url = f"{FHIR_SERVER_URL}/MedicationRequest?_count=100"

    while url:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if 'entry' in data:
            observations.extend(data['entry'])

        url = next((link['url'] for link in data.get('link', []) if link['relation'] == 'next'), None)

    return pd.json_normalize(observations)





def run_pcp_visulization():
    # Fetch data
    patient_data = fetch_all_patients()
    observations_data = fetch_all_observations()
    medication_request = fetch_all_medicationrequest()

    if not patient_data.empty and not observations_data.empty and not medication_request.empty:
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

            # Extracted A1C
            A1C_values = [] 
            if not patient_observations.empty:
                for a1c in patient_observations['resource.code.text']:
                    if isinstance(a1c, str) and "HHb-A1c:" in a1c:
                        A1C_values.append(a1c)

            if A1C_values:
                temp_df['HHb-A1c'] = [', '.join(A1C_values)]
            else:
                temp_df['HHb-A1c'] = ['Unknown']
            
            
            
            # Exracted Glucose
            glu_values = [] 
            glu_interpretation = []
            if not patient_observations.empty:
                if 'resource.valueQuantity.value' in patient_observations:
                    for glu_value in patient_observations['resource.valueQuantity.value']:
                        if glu_value == None:
                            glu_values.append('Unknown')
                        elif glu_value == 0.0:
                            glu_values.append('Normal')
                        elif glu_value == 200.0 or glu_value == 300.0:
                            glu_values.append(f">{glu_values}")
                else:
                    glu_values.append('Unknown')
                
                if 'resource.valueQuantity.interpretation' in patient_observations:
                    # TODO: add test
                    print("Glucose")
                else:
                    glu_interpretation.append('Unknown')
                    # for glu_interp in patient_observations['resource.valueQuantity.interpretation']:
                    #     if glu_interp == None:
                    #         glu_interpretation.append('Unknown')
                    #     elif glu_interp == 'H':
                    #         glu_interpretation.append('High')
                    #     elif glu_interp == 200.0 or glu_value == 300.0:
                    #         glu_values.append(f">{glu_values}")
                    
                    
                    
            if glu_values:
                temp_df['Glucose [Moles/volume] in Blood'] = [', '.join(glu_values)]
            else:
                temp_df['Glucose [Moles/volume] in Blood'] = ['Unknown']
            
            if glu_interpretation:
                temp_df['Glucose [Moles/volume] in Blood Interpretation'] = [', '.join(glu_interpretation)]
            else:
                temp_df['Glucose [Moles/volume] in Blood Interpretation'] = ['Unknown']

            # Initialize medication data for the current patient
            medication_data = {}
            
            
            # Fetch medication usage data for each patient
            patient_medication_request = medication_request[medication_request["resource.subject.reference"] == f"Patient/{id}"]
            
            for i in range(len(patient_medication_request)):
                medication_name = patient_medication_request["resource.medicationCodeableConcept.text"].iloc[i]
                dosage_status = patient_medication_request["resource.dosageInstruction"].iloc[i]
                dosage_status_cleaned = dosage_status[0]['text'].replace('Dosage was ', '') if isinstance(dosage_status, list) and len(dosage_status) > 0 else None
                
                # Extract coding information
                coding_info = patient_medication_request["resource.medicationCodeableConcept.coding"].iloc[i]
                snomed_code = coding_info[0]['code'] if len(coding_info) > 0 else None  # SNOMED code
                rxnorm_code = coding_info[1]['code'] if len(coding_info) > 1 else None  # RxNorm code

                # Construct the medication entry for the current patient
                medication_data[medication_name] = {
                    'snomed': snomed_code,
                    'rxnorm': rxnorm_code,
                    'status': dosage_status_cleaned
                }

            # Add the medication data to the temporary DataFrame as a new column
            temp_df['medication_usage'] = [medication_data]  # Add the medication data to the temp DataFrame

            
            
            # Append the temporary DataFrame to the main DataFrame
            visulization_df = pd.concat([visulization_df, temp_df], ignore_index=True)

    # Export to CSV
    # visulization_df.to_csv("visulization.csv", index=False)

    # ---------------------- Visualization -----------------------------
    # Streamlit application configuration
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

    # Observation
    st.header("Test Results")

    # A1C Test Results Visualization
    with st.expander("A1C Test Results", expanded=True):
        a1c_counts = visulization_df['HHb-A1c'].value_counts().reset_index()
        a1c_counts.columns = ['HHb-A1c', 'Count']
        fig_a1c = px.pie(a1c_counts, values='Count', names='HHb-A1c', title='A1C Test Results Distribution')
        st.plotly_chart(fig_a1c)

    # Glucose Serum Test Results Visualization
    with st.expander("Glucose Serum Test Results", expanded=True):
        glucose_counts = visulization_df['Glucose [Moles/volume] in Blood'].value_counts().reset_index()
        glucose_counts.columns = ['Glucose Test Result', 'Count']
        fig_glucose = px.pie(glucose_counts, values='Count', names='Glucose Test Result', title='Glucose Serum Test Results Distribution')
        st.plotly_chart(fig_glucose)

    # Diagnostics
    # Melt value
    diag_counts = visulization_df.melt(id_vars=['patient_id'], value_vars=['obs_diag_1', 'obs_diag_2', 'obs_diag_3', 'obs_diag_4', 'obs_diag_5', 'obs_diag_6'])

    # Filter those values for other observations
    excluded_values = ['Body weight', 'Glucose [Moles/volume] in Blood', 'Laboratory studies (set)', 'Unknown']
    diag_counts = diag_counts[~diag_counts['value'].isin(excluded_values)]

    # Summary information
    diag_counts = diag_counts['value'].value_counts().reset_index()
    diag_counts.columns = ['Diagnosis', 'Count']

    # Create bar plot
    with st.expander("Diagnosis", expanded=True):
        fig = px.bar(diag_counts, x='Diagnosis', y='Count', 
                    title='Diagnosis Counts', 
                    labels={'Diagnosis': 'Diagnosis', 'Count': 'Count'},
                    color='Count',
                    color_continuous_scale=px.colors.sequential.Blues)

        # Adjust layout for better visibility
        fig.update_layout(
            xaxis_title='Diagnosis', 
            yaxis_title='Count', 
            barmode='group', 
            xaxis_tickangle=-45,
            height=600,  # Increase height for better visibility
            width=800,   # Increase width for better visibility
            margin=dict(l=50, r=50, t=50, b=150)  # Adjust margins to fit labels
        )

        # Show the plot
        st.plotly_chart(fig, use_container_width=True)  # Use container width for responsive design


    # Medicine
    st.header("Medication")
    # Prepare medication usage data
    medication_list = []

    # Iterate over each row in the visualization DataFrame
    for index, row in visulization_df.iterrows():
        patient_id = row['patient_id']  # Extract the patient ID from the row
        medication_usage = row['medication_usage']  # This should be a dict

        # Loop through the medications and their details
        for med_name, details in medication_usage.items():
            status = details['status']
            snomed_code = details.get('snomed', 'N/A')  # Get SNOMED code
            rxnorm_code = details.get('rxnorm', 'N/A')  # Get RxNorm code

            # Get additional patient information
            age = row['age']  # Extract age from the row
            race = row['race']  # Extract race from the row

            # Append medication data with relevant statistics
            medication_list.append({
                'patient_id': patient_id,
                'medication_name': med_name,
                'status': status.strip("{}'"),  # Cleaned status to remove braces and quotes
                'snomed': snomed_code,
                'rxnorm': rxnorm_code,
                'age': age,
                'race': race
            })

    # Create a DataFrame from the medication data
    medication_df = pd.DataFrame(medication_list)

    # Group by medication and status, counting unique patients
    medication_summary = (medication_df
                        .groupby(['medication_name', 'status'])
                        .agg({
                            'patient_id': 'nunique',  # Count unique patient IDs
                            'snomed': 'first',        # Get the first SNOMED code
                            'rxnorm': 'first',        # Get the first RxNorm code
                            'age': lambda x: ', '.join(x.value_counts().index + ' (' + x.value_counts().astype(str) + ')'),  # Summarize age counts
                            'race': lambda x: ', '.join(x.value_counts().index + ' (' + x.value_counts().astype(str) + ')')   # Summarize race counts
                        })
                        .reset_index()
                        .rename(columns={'patient_id': 'Number of Patients'}))

    with st.expander("Medication", expanded=True):
        # Create a grouped bar plot for medication usage
        fig = px.bar(medication_summary, 
                    x='medication_name', 
                    y='Number of Patients', 
                    color='status', 
                    barmode='group', 
                    title='Medication Usage by Status',
                    labels={'medication_name': 'Medication', 'Number of Patients': 'Number of Patients'},
                    hover_data=['status', 'snomed', 'rxnorm', 'age', 'race'])

        # Customize layout
        fig.update_layout(
            xaxis_title='Medication',
            yaxis_title='Number of Patients',
            xaxis_tickangle=-45
        )

        # Display the plot
        st.plotly_chart(fig)