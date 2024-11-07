import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from collections import defaultdict
import plotly.express as px


# FHIR Server
FHIR_SERVER_URL = "http://localhost:3838/fhir"

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

# Streamlit application configuration
st.title("Diabetes Patient Data Visualization")

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

        # Append the temporary DataFrame to the main DataFrame
        visulization_df = pd.concat([visulization_df, temp_df], ignore_index=True)
    
    

# Gender
gender_counts = visulization_df['gender'].value_counts().reset_index()
gender_counts.columns = ['Gender', 'Count']

fig = px.pie(gender_counts, values='Count', names='Gender', title='Gender Distribution')
st.plotly_chart(fig)


# Melt value
diag_counts = visulization_df.melt(id_vars=['patient_id'], value_vars=['obs_diag_1', 'obs_diag_2', 'obs_diag_3', 'obs_diag_4', 'obs_diag_5', 'obs_diag_6'])

# filter those values for other obs
excluded_values = ['Body weight', 'Glucose [Moles/volume] in Blood', 'Laboratory studies (set)', 'Unknown']
diag_counts = diag_counts[~diag_counts['value'].isin(excluded_values)]

# summary information
diag_counts = diag_counts['value'].value_counts().reset_index()
diag_counts.columns = ['Diagnosis', 'Count']

# create bar plot
fig = px.bar(diag_counts, x='Diagnosis', y='Count', title='Diagnosis Counts', color='Count')
st.plotly_chart(fig)

# scatter plot

fig = px.scatter(visulization_df, x='age', y='HHb-A1c', title='Age vs HHb-A1c', hover_data=['patient_id'])
st.plotly_chart(fig)
    
    # Print the complete visulization_df
    # print(visulization_df)


#
    
    # # Merge patient data with observations data
    # merged_data = pd.merge(patient_data, observations_data, left_on='resource.id', right_on='patient_id', how='outer')
    # print(merged_data["resource.id_x"])
    
    # # Group by patient to consolidate observations
    # # This will create a new DataFrame with unique patients and their corresponding observations
    # merged_data = merged_data.groupby('resource.id_x').agg({
    #     'resource.gender_x': 'first',
    #     'resource.extension_y': lambda x: list(x.dropna()),  # Collect all extensions into a list
    #     'patient_id_y': 'first'  # Keep the first patient_id
    # }).reset_index()

    # # Optional: Flatten the list of extensions to make it easier to access
    # merged_data['weight_ranges'] = merged_data['resource.extension'].apply(lambda x: [ext for ext in x if ext.get('url') == 'http://hl7.org/fhir/StructureDefinition/observation-weight-range'])
    # merged_data['diagnostics'] = merged_data['resource.extension'].apply(lambda x: [ext for ext in x if ext.get('url') != 'http://hl7.org/fhir/StructureDefinition/observation-weight-range'])

    # # Drop the original extension column if you no longer need it
    # merged_data.drop(columns=['resource.extension'], inplace=True)

    










# # Check if patient data is available
# if not patient_data.empty:
#     patient_weight_diag_mapping = defaultdict(lambda: [[], []])  # patient_id: [[weight_ranges], [diagnostics]]

#     # Process observations
#     if not observations_data.empty:
#         for index, row in observations_data.iterrows():
#             # Get subject patient ID
#             subject_ref = row['resource.subject.reference']
#             patient_id = subject_ref.split('/')[-1]  # Extract ID

#             # Process weight ranges
#             extensions = row.get('resource.extension', [])
#             low_value = None
#             high_value = None

#             for ext in extensions:
#                 if ext.get('url') == 'http://hl7.org/fhir/StructureDefinition/observation-weight-range':
#                     value_quantity = ext.get('valueQuantity', {})
#                     weight_value = value_quantity.get('value', None)

#                     if weight_value is not None:
#                         if low_value is None:
#                             low_value = weight_value
#                         else:
#                             high_value = weight_value

#             if low_value is not None and high_value is not None:
#                 patient_weight_diag_mapping[patient_id][0].append((low_value, high_value))  # Append weight range

#             # Process diagnostics
#             diag_columns = ['diag_1', 'diag_2', 'diag_3']
#             diagnostics = []
#             for diag_col in diag_columns:
#                 concept_code = row['resource'].get(diag_col)  # Adjust if needed to access the correct key
#                 if concept_code:
#                     diagnostics.append(concept_code)

#             if diagnostics:
#                 patient_weight_diag_mapping[patient_id][1].extend(diagnostics)  # Append diagnostics

#     # Output the mapping for debugging
#     print(patient_weight_diag_mapping)

#     # Visualization or further processing can be done here

#     # Example to show the structure in Streamlit
#     for patient_id, (weight_ranges, diagnostics) in patient_weight_diag_mapping.items():
#         st.write(f"Patient ID: {patient_id}")
#         st.write(f"Weight Ranges: {weight_ranges}")
#         st.write(f"Diagnostics: {diagnostics}")

# else:
#     st.write("No patient information extracted.")
