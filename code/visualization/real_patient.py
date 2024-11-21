import streamlit as st
import pandas as pd
import json
import os
import plotly.express as px
from datetime import datetime
import re

# Function to load and process JSON files
@st.cache_resource
def load_patient_data(directory):
    patient_list = []
    bmi_data = []
    
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            with open(os.path.join(directory, filename), "r") as file:
                data = json.load(file)
                
                for entry in data.get('entry', []):
                    resource = entry.get('resource', {})
                    
                    # Extract patient information
                    if resource.get('resourceType') == 'Patient':
                        patient = {}
                        
                        # Function to remove numeric suffixes
                        def clean_name(name):
                            return re.sub(r'\d+$', '', name)  # Remove trailing numbers
                        
                        # Extract name
                        name_data = resource.get('name', [{}])[0]
                        given_names = name_data.get('given', [])
                        family_name = name_data.get('family', '')
                        # Clean each part of the name
                        clean_given_names = [clean_name(name) for name in given_names]
                        clean_family_name = clean_name(family_name)

                        # Combine cleaned names
                        patient['Name'] = ' '.join(clean_given_names + [clean_family_name])
                        # patient['Name'] = ' '.join(given_names + [family_name])
                        
                        # Extract birth date
                        # patient['BirthDate'] = resource.get('birthDate', None)
                        # Extract birth date and calculate age
                        birth_date_str = resource.get('birthDate', None)
                        patient['BirthDate'] = birth_date_str
                        if birth_date_str:
                            birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d')  # Convert birth date string to a datetime object
                            current_year = datetime.now().year  # Get the current year
                            patient['Age'] = current_year - birth_date.year
                            # Adjust for cases where the birth date hasn't yet occurred in the current year
                            if datetime.now().month < birth_date.month or (datetime.now().month == birth_date.month and datetime.now().day < birth_date.day):
                                patient['Age'] -= 1
                        else:
                            patient['Age'] = "Unknown"  # Default if birth date is not available
                        
                        # Extract gender
                        patient['Gender'] = resource.get('gender', None)
                        
                        # Extract race
                        race_extension = next(
                            (ext for ext in resource.get('extension', []) if 'us-core-race' in ext.get('url', '')),
                            {}
                        )                                            
                        race_coding = race_extension.get('extension', [{}])[0]
                        patient['Race'] = race_coding.get('valueCoding', {}).get('display', None)
                        
                        # Extract address
                        address_data = resource.get('address', [{}])[0]
                        if address_data:
                            line = ", ".join(address_data.get("line", []))
                            city = address_data.get("city", "Unknown")
                            state = address_data.get("state", "Unknown")
                            postal_code = address_data.get("postalCode", "Unknown")
                            country = address_data.get("country", "Unknown")
                            patient['Address'] = f"{line}, {city}, {state}, {postal_code}, {country}"
                        else:
                            patient['Address'] = "Unknown"
                        
                        
                        # Save patient information
                        patient['ID'] = resource.get('id', '')
                        patient_list.append(patient)
                    
                    # Extract BMI data
                    if resource.get('resourceType') == 'Observation' and resource.get('code', {}).get('coding', [{}])[0].get('code') == '39156-5':
                        bmi_entry = {
                            'PatientID': resource['subject']['reference'].split(":")[-1],
                            'EncounterID': resource['encounter']['reference'].split(":")[-1],
                            'BMIValue': resource.get('valueQuantity', {}).get('value', None),
                            'Unit': resource.get('valueQuantity', {}).get('unit', None)
                        }
                        bmi_data.append(bmi_entry)

    return pd.DataFrame(patient_list), pd.DataFrame(bmi_data)


# Add human-readable encounter labels
def assign_encounter_labels(bmi_df):
    bmi_df = bmi_df.copy()
    bmi_df["EncounterNumber"] = bmi_df.groupby("PatientID").cumcount() + 1
    bmi_df["EncounterLabel"] = bmi_df["EncounterNumber"].apply(lambda x: f"Encounter{x}")
    return bmi_df

def run_real_patient_visulization(user_id):
    # Define available user directories
    dir = os.getcwd()
    user_data_directories = {
        "Winnie": os.path.join(dir,"synthea","Winnie") #"../../synthea/Winnie",
        "Yi": "../../synthea/Yi"
    }
    # st.write(os.getcwd())
    # Check if user ID is valid and data directory exists
    if user_id not in user_data_directories or not os.path.exists(user_data_directories[user_id]):
        st.title(f"Welcome Dr. {user_id}")
        st.warning("There are no available patient information for you.")
        return

    # Load patient data
    data_directory = user_data_directories[user_id]
    patient_df, bmi_df = load_patient_data(data_directory)
    bmi_df = assign_encounter_labels(bmi_df)


    # Streamlit App
    st.title("Patient Overview")

    # Sidebar: Dropdown for patient selection
    st.empty()
    st.sidebar.header("Patient Selection")
    patient_names = patient_df["Name"].unique().tolist()
    selected_patient = st.sidebar.selectbox("Choose a Patient", options=patient_names)

    # Main Panel
    if selected_patient:
        # Filter data for selected patient
        selected_patient_data = patient_df[patient_df["Name"] == selected_patient].iloc[0]
        selected_patient_bmi = bmi_df[bmi_df["PatientID"] == selected_patient_data["ID"]]
        
        # Display patient details
        st.subheader(f"Patient Details: {selected_patient}")
        st.markdown(f"- **Birth Date**: {selected_patient_data['BirthDate'] or 'None'}")
        st.markdown(f"- **Age**: {selected_patient_data['Age'] or 'None'}")
        st.markdown(f"- **Gender**: {selected_patient_data['Gender'] or 'None'}")
        st.markdown(f"- **Race**: {selected_patient_data['Race'] or 'None'}")
        st.markdown(f"- **Address**: {selected_patient_data['Address'] or 'None'}")

        
        # Check if BMI data is available for the patient
        if not selected_patient_bmi.empty:
            # Sort BMI records by EncounterNumber
            selected_patient_bmi = selected_patient_bmi.sort_values("EncounterNumber")
            
            # Scatter Plot with Trend Line
            st.subheader("BMI Trend Across Encounters")
            fig = px.scatter(
                selected_patient_bmi,
                x="EncounterLabel",
                y="BMIValue",
                title="BMI Trend Across Encounters",
                labels={"EncounterLabel": "Encounter", "BMIValue": "BMI Value"},
                text="BMIValue"
            )
            # Add a trend line by connecting the dots
            fig.update_traces(mode='lines+markers')
            fig.update_layout(
                xaxis_title="Encounter",
                yaxis_title="BMI Value (kg/m2)",
                height=500,
                width=800
            )
            st.plotly_chart(fig)

            # Table of BMI Values
            st.subheader("BMI Values Table")
            st.table(
                selected_patient_bmi[["EncounterLabel", "BMIValue"]].rename(
                    columns={"EncounterLabel": "Encounter", "BMIValue": "BMI Value (kg/m2)"}
                )
            )
        else:
            st.warning("No BMI data available for this patient.")
    else:
        st.warning("Please select a patient to view their BMI trend.")
