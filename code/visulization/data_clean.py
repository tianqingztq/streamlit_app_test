import pandas as pd

def remove_duplicates(dataframe):
    """
    Remove duplicate rows based on the 'patient_nbr' column in the given DataFrame.
    
    Parameters:
        dataframe (pd.DataFrame): The input DataFrame containing patient data.
    
    Returns:
        pd.DataFrame: DataFrame with duplicates removed.
    """
    # Remove duplicate patient_nbr rows
    dataframe_deduplicated = dataframe.drop_duplicates(subset='patient_nbr', keep='first')
    
    return dataframe_deduplicated

def clean_gender(dataframe):
    """
    Clean the 'Gender' column in the given DataFrame to match FHIR R4 standards.
    
    Parameters:
        dataframe (pd.DataFrame): The input DataFrame containing patient data.
    
    Returns:
        pd.DataFrame: DataFrame with cleaned 'gender' values.
    """
    gender_mapping = {
        'Female': 'female',
        'Male': 'male',
        'Unknown/Invalid': 'unknown',
    }
    
    dataframe['gender'] = dataframe['gender'].replace(gender_mapping).fillna('unknown')
    
    return dataframe


def clean_race(dataframe):
    """
    Clean the 'Gender' column in the given DataFrame to match FHIR R4 standards.

    Parameters:
        dataframe (pd.DataFrame): The input DataFrame containing patient data.
    
    Returns:
        pd.DataFrame: DataFrame with cleaned 'race' values.
    """
    race_mapping = {
        '?': 'Unknown',
        'Caucasian': 'White',
        'AfricanAmerican': 'Black or African American',
        'Hispanic': 'Hispanic or Latino',
        'Asian': 'Asian',
        'Other': 'Other'
    }
    
    dataframe['race'] = dataframe['race'].replace(race_mapping)
    return dataframe

def clean_age(dataframe):
    """
    Clean the 'age' column in the given DataFrame to match FHIR R4 standards.
    
    Parameters:
        dataframe (pd.DataFrame): The input DataFrame containing patient data.
    
    Returns:
        pd.DataFrame: DataFrame with cleaned 'age' values.
    """
    age_mapping = {
        '[0-10)': 'P0Y-P10Y',
        '[10-20)': 'P10Y-P20Y',
        '[20-30)': 'P20Y-P30Y',
        '[30-40)': 'P30Y-P40Y',
        '[40-50)': 'P40Y-P50Y',
        '[50-60)': 'P50Y-P60Y',
        '[60-70)': 'P60Y-P70Y',
        '[70-80)': 'P70Y-P80Y',
        '[80-90)': 'P80Y-P90Y',
        '[90-100)': 'P90Y-P9999Y',
    }
    
    # Replace age ranges with FHIR format
    dataframe['age'] = dataframe['age'].replace(age_mapping)
    
    # Return the modified DataFrame
    return dataframe


# ----------- Observation -----------
def pounds_to_kg(pounds):
    # Pounds to kg
    return pounds * 0.453592


def clean_weight(dataframe):
    # Create new list
    cleaned_weights = []

    # clean 'weight column'
    for weight in dataframe['weight']:
        if weight == '[0-25)':
            cleaned_weights.append({'value': {'low': pounds_to_kg(0), 'high': pounds_to_kg(25)}, 'unit': 'kg'})
        elif weight == '[25-50)':
            cleaned_weights.append({'value': {'low': pounds_to_kg(25), 'high': pounds_to_kg(50)}, 'unit': 'kg'})
        elif weight == '[50-75)':
            cleaned_weights.append({'value': {'low': pounds_to_kg(50), 'high': pounds_to_kg(75)}, 'unit': 'kg'})
        elif weight == '[75-100)':
            cleaned_weights.append({'value': {'low': pounds_to_kg(75), 'high': pounds_to_kg(100)}, 'unit': 'kg'})
        elif weight == '[100-125)':
            cleaned_weights.append({'value': {'low': pounds_to_kg(100), 'high': pounds_to_kg(125)}, 'unit': 'kg'})
        elif weight == '[125-150)':
            cleaned_weights.append({'value': {'low': pounds_to_kg(125), 'high': pounds_to_kg(150)}, 'unit': 'kg'})
        elif weight == '[150-175)':
            cleaned_weights.append({'value': {'low': pounds_to_kg(150), 'high': pounds_to_kg(175)}, 'unit': 'kg'})
        elif weight == '[175-200)':
            cleaned_weights.append({'value': {'low': pounds_to_kg(175), 'high': pounds_to_kg(200)}, 'unit': 'kg'})
        elif weight == '>200':
            cleaned_weights.append({'value': {'low': pounds_to_kg(200), 'high': None}, 'unit': 'kg'})
        elif weight == '?':
            cleaned_weights.append({'value': None, 'unit': None})  
        else:
            cleaned_weights.append({'value': None, 'unit': None})  

    # Add into new column
    dataframe['weight_fhir'] = cleaned_weights

    return dataframe

def convert_icd9_to_concept(dataframe, concept_file_path):
    
    concept_df = pd.read_csv(concept_file_path, sep = "\t")

    
    concept_mapping = dict(zip(concept_df['concept_code'], concept_df['concept_name']))
    concept_id_mapping = dict(zip(concept_df['concept_code'], concept_df['concept_id']))

    diag_columns = ['diag_1', 'diag_2', 'diag_3']

    dataframe[diag_columns] = dataframe[diag_columns].replace('?', None)
    
    for diag_col in diag_columns:
        
        dataframe[f'{diag_col}_concept'] = dataframe[diag_col].map(concept_mapping)
        dataframe[f'{diag_col}_concept_id'] = dataframe[diag_col].map(concept_id_mapping)

    
    return dataframe
