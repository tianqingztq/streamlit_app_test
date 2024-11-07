import pandas as pd
import requests
from fhirclient import client
from fhirclient.models.patient import Patient
from fhirclient.models.encounter import Encounter, EncounterHospitalization
from fhirclient.models.observation import Observation
from fhirclient.models.medicationstatement import MedicationStatement
from fhirclient.models.fhirreference import FHIRReference
from fhirclient.models.extension import Extension
from fhirclient.models.coding import Coding
from fhirclient.models.codeableconcept import CodeableConcept
from fhirclient.models.quantity import Quantity
from fhirclient.models.narrative import Narrative
from fhirclient.models.meta import Meta


from data_clean import (
    remove_duplicates,
    clean_gender,
    clean_race,
    clean_age,
    pounds_to_kg,
    clean_weight,
    convert_icd9_to_concept
)

# Use public server URL
FHIR_SERVER_URL = "http://localhost:3838/fhir"

# FHIR serve settings
settings = {
    'app_id': 'my_app',
    'api_base': FHIR_SERVER_URL
}
smart = client.FHIRClient(settings=settings)

# load data
data = pd.read_csv('/Users/winniez/Desktop/Gatech/Gatech_OMSCS/CS6440/Group_project/CS6440-Project/kaggle_data/visulization/diabetic_data_test.csv')

# Apply data cleaning functions
data = remove_duplicates(data)
data = clean_gender(data)
data = clean_race(data)
data = clean_age(data)
data = clean_weight(data)
data = convert_icd9_to_concept(data, "/Users/winniez/Desktop/Gatech/Gatech_OMSCS/CS6440/Group_project/CS6440-Project/kaggle_data/visulization/ICD9CM/CONCEPT.csv")

# Create patient resource
def create_patient_resource(row):
    patient = Patient()
    patient.id = str(row['patient_nbr'])
    patient.gender = str(row['gender'])

    # create extension
    extensions = []
    # Age
    if pd.notna(row['age']):
        age_value = str(row['age'])
        age_extension = Extension({
            'url': 'age',
            'valueString': age_value
        })
        extensions.append(age_extension)

    # Race
    if pd.notna(row['race']):
        race_value = row['race']
        race_mapping = {
            'White': {'code': '2106-3', 'display': 'White'},
            'Black or African American': {'code': '2054-5', 'display': 'Black or African American'},
            'Hispanic or Latino': {'code': '2131-1', 'display': 'Hispanic or Latino'},
            'Asian': {'code': '2028-9', 'display': 'Asian'},
            'Other': {'code': '2131-1', 'display': 'Other'}, 
            'Unknown': {'code': None, 'display': 'Unknown'}
        }
        race_code = race_mapping.get(race_value, None)
        
        if race_code:
            race_extension = Extension({
                'url': 'ombCategory', 
                'valueCoding': {
                    'system': 'urn:oid:2.16.840.1.113883.6.238',
                    'code': race_code['code'],
                    'display': race_code['display']
                }
            })
            extensions.append(race_extension)
            

    patient.extension = extensions
    return patient

# create Encounter resource
# def create_encounter_resource(row):
#     encounter = Encounter()
#     encounter.id = str(row['encounter_id'])
#     encounter.status = "finished"
#     encounter.subject = FHIRReference({"reference": f"Patient/{row['patient_nbr']}"})

#     encounter.class_fhir = Coding()
#     encounter.class_fhir.system = "http://terminology.hl7.org/CodeSystem/v3-ActCode"
#     encounter.class_fhir.code = str(row['admission_type_id'])
#     encounter.class_fhir.display = "admission type"

#     hospitalization = EncounterHospitalization()
#     discharge_disposition = CodeableConcept()
#     discharge_disposition.coding = [
#         Coding({
#             "system": "http://terminology.hl7.org/CodeSystem/discharge-disposition",
#             "code": str(row['discharge_disposition_id']),
#             "display": "discharge disposition"
#         })
#     ]
#     hospitalization.dischargeDisposition = discharge_disposition
    
#     encounter.hospitalization = hospitalization
#     return encounter

# Create Observation resource
def create_observation_resources(row):
    observations = []

    
    diag_columns = ['diag_1', 'diag_2', 'diag_3']
    
    # Iterate whole diag columns
    for diag_col in diag_columns:
        concept_code = row[f'{diag_col}']
        concept_name = row[f'{diag_col}_concept']  
        concept_id = row[f'{diag_col}_concept_id']
        
        
        if pd.notna(concept_code):
            observation = Observation()
            observation.status = "final"
            observation.subject = FHIRReference({"reference": f"Patient/{row['patient_nbr']}"})

            code_concept = CodeableConcept()
            coding = Coding()
            coding.system = "http://hl7.org/fhir/sid/us-icd-9"  # ICD-9
            coding.code = concept_code  # 
            coding.display = concept_name  # Concept Name as display value
            code_concept.coding = [coding]
            observation.code = code_concept
            
            observations.append(observation)

    # Weight observation
    weight_value = row.get('weight_fhir')  # Safely access the weight value
    if isinstance(weight_value, dict) and weight_value.get('value') is not None:
        weight_data = weight_value['value']
        
        weight_observation = Observation()
        weight_observation.status = "final"
        weight_observation.subject = FHIRReference({"reference": f"Patient/{row['patient_nbr']}"})

        # Set weight code concept
        weight_code_coding = Coding()
        weight_code_coding.system = 'http://loinc.org'
        weight_code_coding.code = '29463-7'  # LOINC code for Body weight
        weight_code_coding.display = 'Body weight'

        weight_code_concept = CodeableConcept()
        weight_code_concept.coding = [weight_code_coding]
        weight_observation.code = weight_code_concept
        
        # Instead of using valueQuantity directly, we create extensions to capture the range
        weight_observation.extension = [
            Extension({
                'url': 'http://hl7.org/fhir/StructureDefinition/observation-weight-range',
                'valueQuantity': {
                    'value': weight_data['low'],  # Lower limit
                    'unit': weight_value['unit'],
                    'system': 'http://unitsofmeasure.org',  # Unit system
                    'code': weight_value['unit']  # Weight unit
                }
            }),
            Extension({
                'url': 'http://hl7.org/fhir/StructureDefinition/observation-weight-range',
                'valueQuantity': {
                    'value': weight_data['high'],  # Upper limit
                    'unit': weight_value['unit'],
                    'system': 'http://unitsofmeasure.org',  # Unit system
                    'code': weight_value['unit']  # Weight unit
                }
            })
        ]
            
        observations.append(weight_observation)

    # A1C observation
    a1c_value = row.get('A1Cresult')  # Access the A1C result
    a1c_observation = Observation()
    a1c_observation.status = "final"
    a1c_observation.subject = FHIRReference({"reference": f"Patient/{row['patient_nbr']}"})
    
    # Setting the ID for the observation
    # a1c_observation.id = "HbA1c"

    # # Meta and Profile
    meta = Meta()
    meta.profile = ["http://fhir.ch/ig/ch-etoc/StructureDefinition/ch-etoc-lab-observation"]
    a1c_observation.meta = meta
    
    # Coding for A1C
    a1c_code_coding = Coding()
    a1c_code_coding.system = 'http://loinc.org'
    a1c_code_coding.code = '26436-6'  # Use appropriate LOINC code for A1C
    a1c_code_coding.display = 'Laboratory studies (set)'

    
    if pd.notna(a1c_value): 
        if a1c_value == "Norm":
            a1c_display_value = "HHb-A1c: Norm"
        elif a1c_value is None:
            a1c_display_value = "HHb-A1c: None"
        else:  # Handle cases like '>7', '>8', etc.
            a1c_display_value = f"HHb-A1c: {a1c_value} %"
        
        a1c_code_concept = CodeableConcept()
        a1c_code_concept.coding = [a1c_code_coding]
        a1c_code_concept.text = a1c_display_value  # Set the text representation in the code

        a1c_observation.code = a1c_code_concept  # Assign the code to the observation
        # Narrative text (optional)
        a1c_observation.text = Narrative({
            "status": "generated",
            "div": f"<div xmlns=\"http://www.w3.org/1999/xhtml\">" \
                    f"<p class=\"res-header-id\"><b>Generated Narrative: Observation HbA1c</b></p>" \
                    f"<p><b>status</b>: Final</p>" \
                    f"<p><b>code</b>: <span title=\"Codes:{{http://loinc.org 26436-6}}\">{a1c_display_value}</span></p>" \
                    f"<p><b>subject</b>: <a href=\"Patient-{row['patient_nbr']}.html\">Patient Identifier (official)</a></p>" \
                    f"</div>"
        })

    else:
        a1c_display_value = "HHb-A1c: None"
        a1c_code_concept = CodeableConcept()
        a1c_code_concept.coding = [a1c_code_coding]
        a1c_code_concept.text = a1c_display_value  # Set the text representation in the code

        a1c_observation.code = a1c_code_concept  # Assign the code to the observation
        # Narrative text (optional)
        a1c_observation.text = Narrative({
            "status": "generated",
            "div": f"<div xmlns=\"http://www.w3.org/1999/xhtml\">" \
                    f"<p class=\"res-header-id\"><b>Generated Narrative: Observation HbA1c</b></p>" \
                    f"<p><b>status</b>: Final</p>" \
                    f"<p><b>code</b>: <span title=\"Codes:{{http://loinc.org 26436-6}}\">{a1c_display_value}</span></p>" \
                    f"<p><b>subject</b>: <a href=\"Patient-{row['patient_nbr']}.html\">Patient Identifier (official)</a></p>" \
                    f"</div>"
        })
    observations.append(a1c_observation)

    # Glucose Serum observation
    glucose_value = row.get('max_glu_serum')  # Access the max glucose serum value
    glucose_observation = Observation()
    glucose_observation.status = "final"
    glucose_observation.subject = FHIRReference({"reference": f"Patient/{row['patient_nbr']}"})

    glucose_code_coding = Coding()
    glucose_code_coding.system = 'http://loinc.org'
    glucose_code_coding.code = '15074-8'  # LOINC code for Glucose [Mass/volume] in Serum or Plasma
    glucose_code_coding.display = 'Glucose [Moles/volume] in Blood'

    glucose_code_concept = CodeableConcept()
    glucose_code_concept.coding = [glucose_code_coding]
    glucose_observation.code = glucose_code_concept
    
    if pd.notna(glucose_value):
        # Handle the value of Glucose Serum
        glucose_value_display = "Unknown" if glucose_value is None else glucose_value
        
        if glucose_value_display == ">300":
            glucose_observation.valueQuantity = Quantity({
                "value": 300,  # Set to 300 for >300
                "unit": "mg/dL",
                "system": "http://unitsofmeasure.org",  # Unit system
                "code": "mg/dL"
            })
            glucose_observation.interpretation = [CodeableConcept({
                'coding': [Coding({
                    'system': "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
                    'code': "H>",  # High
                    'display': "Significantly high"
                })]
            })]
        elif glucose_value_display == ">200":
            glucose_observation.valueQuantity = Quantity({
                "value": 200,  # Set to 200 for 200
                "unit": "mg/dL",
                "system": "http://unitsofmeasure.org",  # Unit system
                "code": "mg/dL"
            })
            glucose_observation.interpretation = [CodeableConcept({
                'coding': [Coding({
                    'system': "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
                    'code': "H",  # High
                    'display': "High"
                })]
            })]
        elif glucose_value_display == "Norm":
            glucose_observation.valueQuantity = Quantity({
                "value": 0,  # Set to 0 for Normal
                "unit": "mg/dL",
                "system": "http://unitsofmeasure.org",  # Unit system
                "code": "mg/dL"
            })
            glucose_observation.interpretation = [CodeableConcept({
                'coding': [Coding({
                    'system': "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
                    'code': "N",  # Normal
                    'display': "Normal"
                })]
            })]
        
    else:
        glucose_value_display = "Unknown" if glucose_value is None else glucose_value
        
        glucose_observation.valueQuantity = Quantity({
            "value": None,
            "unit": "mg/dL",
            "system": "http://unitsofmeasure.org",  # Unit system
            "code": "mg/dL"
        })
        
    
    observations.append(glucose_observation)
    
    
    return observations



# Create MedicationStatement Resource
# def create_medication_statement(row, medication):
#     med_statement = MedicationStatement()
#     med_statement.status = "active" if row[medication] == "Steady" else "completed"
    
#     medication_concept = CodeableConcept()
#     medication_coding = Coding()
#     medication_coding.system = "http://www.nlm.nih.gov/research/umls/rxnorm"
#     medication_coding.display = medication
#     medication_concept.coding = [medication_coding]
#     med_statement.medicationCodeableConcept = medication_concept

#     med_statement.subject = FHIRReference({"reference": f"Patient/{row['patient_nbr']}"})
#     return med_statement

# Upload resource batch
def upload_batch_to_fhir(batch_resources):
    batch_request = {
        "resourceType": "Bundle",
        "type": "transaction",
        "entry": [
            {"resource": resource.as_json(), "request": {"method": "POST", "url": resource.resource_type}}
            for resource in batch_resources
        ]
    }
    response = requests.post(FHIR_SERVER_URL, json=batch_request)
    response.raise_for_status()
    return response.json()

# Upload into HAPI FHIR server
def upload_resources(data, batch_size=100):
    batch_resources = []
    for _, row in data.iterrows():
        # Add and create Patient resource
        batch_resources.append(create_patient_resource(row))
        
        # Add and create Observation resources
        observation_resources = create_observation_resources(row)
        batch_resources.extend(observation_resources)

        # Add and create Encounter resource
        # batch_resources.append(create_encounter_resource(row))

        # Add and create Observation resource
        # observations = {
        #     "max_glu_serum": row['max_glu_serum'],
        #     "A1Cresult": row['A1Cresult'],
        #     "num_lab_procedures": row['num_lab_procedures'],
        #     "num_procedures": row['num_procedures'],
        #     "num_medications": row['num_medications'],
        #     "number_outpatient": row['number_outpatient'],
        #     "number_emergency": row['number_emergency'],
        #     "number_inpatient": row['number_inpatient'],
        #     "number_diagnoses": row['number_diagnoses']
        # }
        # for obs_type, value in observations.items():
        #     if pd.notna(value):
        #         batch_resources.append(create_observation_resource(row, obs_type, value))

        # Add and create MedicationStatement resource
        # medications = [
        #     'metformin', 'repaglinide', 'nateglinide', 'chlorpropamide', 'glimepiride',
        #     'acetohexamide', 'glipizide', 'glyburide', 'tolbutamide', 'pioglitazone',
        #     'rosiglitazone', 'acarbose', 'miglitol', 'troglitazone', 'tolazamide',
        #     'insulin', 'glyburide-metformin', 'glipizide-metformin', 
        #     'glimepiride-pioglitazone', 'metformin-rosiglitazone', 'metformin-pioglitazone'
        # ]
        # for med in medications:
        #     if row[med] != "No":
        #         batch_resources.append(create_medication_statement(row, med))

        # Batch upload
        if len(batch_resources) >= batch_size:
            upload_batch_to_fhir(batch_resources)
            batch_resources = []

    # Batch upload
    if batch_resources:
        upload_batch_to_fhir(batch_resources)

# Run

upload_resources(data)
