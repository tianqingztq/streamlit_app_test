import streamlit as st
import psycopg2
from werkzeug.security import generate_password_hash, check_password_hash
import os
from visualization.visulization import run_patient_visulization
from visualization.visulization import run_pcp_visulization
from visualization.real_patient import run_real_patient_visulization
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from st_files_connection import FilesConnection
import pandas as pd
import pickle
import joblib

DB_HOST=os.environ['DB_HOST']
DB_NAME=os.environ['DB_NAME']
DB_USER=os.environ['DB_USER']
DB_PASS=os.environ['DB_PASS']




def apply_custom_styles():
    st.markdown("""
        <style>
            /* Global Styles */
            .main {
                background-color: white;
            }
            
            .main > div {
                padding: 2rem;
                max-width: 1200px;
                margin: 0 auto;
            }
            
            /* Typography */
            h1, h2, h3, h4, h5, h6 {
                font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif;
                color: #1a1f36;
            }
            
            p, li {
                font-family: -apple-system, BlinkMacSystemFont, sans-serif;
                color: #4a5568;
            }
            
            /* Main Title Styles */
            .main-title {
                color: #1a1f36;
                font-size: 3rem;
                font-weight: 700;
                text-align: center;
                margin-bottom: 1rem;
                line-height: 1.2;
            }
            
            .subtitle {
                color: #4a5568;
                font-size: 1.2rem;
                text-align: center;
                margin-bottom: 3rem;
                line-height: 1.6;
            }
            
            /* Card Styles */
            .card {
                background: white;
                border-radius: 12px;
                padding: 2.5rem;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
                height: 100%;
                display: flex;
                flex-direction: column;
                align-items: center;
                text-align: center;
                transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
                border: 1px solid #e5e7eb;
            }
            
            .card:hover {
                transform: translateY(-5px);
                box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
            }
            
            .card-title {
                color: #1a1f36;
                font-size: 1.8rem;
                font-weight: 600;
                margin-bottom: 1.25rem;
            }
            
            .card-text {
                color: #4a5568;
                font-size: 1.1rem;
                margin-bottom: 2rem;
                line-height: 1.6;
            }
            
            /* Button Styles */
            .stButton > button {
                background-color: #0066ff;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 0.875rem 1.75rem;
                font-size: 1.1rem;
                font-weight: 500;
                width: 100%;
                transition: all 0.2s ease-in-out;
                box-shadow: 0 2px 4px rgba(0, 102, 255, 0.1);
            }
            
            .stButton > button:hover {
                background-color: #0052cc;
                transform: translateY(-1px);
                box-shadow: 0 4px 6px rgba(0, 102, 255, 0.2);
            }
            
            /* Form Styles */
            .stRadio > label, .stSelectbox > label {
                color: #1a1f36;
                font-weight: 500;
                font-size: 1.1rem;
                margin-bottom: 0.5rem;
            }
            
            /* Survey Section Styles */
            .survey-section {
                background: white;
                padding: 2rem;
                border-radius: 12px;
                margin-bottom: 2rem;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
                border: 1px solid #e5e7eb;
            }
            
            /* Fix Streamlit Form Background */
            .stForm {
                background-color: white !important;
            }
            
            section[data-testid="stSidebar"] {
                background-color: white;
            }
            
            /* Remove Streamlit Default Elements */
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            .main > div:first-child {padding-top: 1rem;}
            
            /* Streamlit Elements Background Fix */
            div[data-testid="stToolbar"],
            div[data-testid="stDecoration"],
            div[data-testid="stStatusWidget"] {
                background-color: white !important;
            }
            
            div[class*="css"] {
                background-color: white !important;
            }
            
            div[data-testid="stMarkdownContainer"] {
                background-color: white !important;
            }
            
            .streamlit-expanderHeader {
                background-color: white !important;
            }
            
            .stRadio > div {
                background-color: white !important;
            }
            
            .stTabs > div {
                background-color: white !important;
            }
            
            /* Divider color */
            hr {
                border-color: #e5e7eb;
            }
        </style>
    """, unsafe_allow_html=True)

def init_db():
    """Initialize database connection and create tables if they don't exist"""
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )
    cur = conn.cursor()
    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS hcps (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            full_name VARCHAR(255) NOT NULL,
            license_number VARCHAR(50) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create survey_results table
    #cur.execute('''drop table if exists survey_results''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS survey_results (
            id SERIAL PRIMARY KEY,
            high_blood_pressure INTEGER,
            high_cholesterol INTEGER,
            cholesterol_check INTEGER,
            bmi FLOAT,
            smoking INTEGER,
            stroke INTEGER,
            heart_disease INTEGER,
            physical_activity INTEGER,
            fruit_consumption INTEGER,
            vegetable_consumption INTEGER,
            heavy_drinker INTEGER,
            healthcare_coverage INTEGER,
            doctor_cost_barrier INTEGER,
            general_health INTEGER,
            mental_health INTEGER,
            physical_health INTEGER,
            difficulty_walking INTEGER,
            gender INTEGER,
            age INTEGER,
            education INTEGER,
            income INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    return conn

def load_ml_model():
    """Load the pre-trained machine learning model pickle file"""
    try:
        # Load the model from pickle file
        #with open('./ML_model/final_model.pkl', 'rb') as model_file:
        st_conn = st.connection('gcs', type=FilesConnection)
        with st_conn.open(
            'streamlit-bucket-tq/rf_model.pkl', 
            #'streamlit-bucket-tq/xgboost_model.pkl', 
            'rb') as model_file:
            model = pickle.load(model_file)
        return model
    except Exception as e:
        st.error(f"Error loading model: {e}")
        return None, None


def get_latest_survey_result(conn):
    """Retrieve the latest survey result from the database"""
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT 
                high_blood_pressure, high_cholesterol, cholesterol_check, 
                bmi, smoking, stroke, heart_disease, physical_activity,
                fruit_consumption, vegetable_consumption, heavy_drinker,
                healthcare_coverage, doctor_cost_barrier, general_health,
                mental_health, physical_health, difficulty_walking,
                gender, age, education, income
            FROM survey_results 
            ORDER BY created_at DESC 
            LIMIT 1
        """)
        result = cur.fetchone()
        if result:
            # Convert to dictionary with column names
            columns = [
                'HighBP', 'HighChol', 'CholCheck',
                'BMI', 'Smoker', 'Stroke', 'HeartDiseaseorAttack', 'PhysActivity',
                'Fruits', 'Veggies', 'HvyAlcoholConsump',
                'AnyHealthcare', 'NoDocbcCost', 'GenHlth',
                'MentHlth', 'PhysHlth', 'DiffWalk',
                'Sex', 'Age', 'Education', 'Income'
            ]
            return dict(zip(columns, result))
        return None
    except Exception as e:
        st.error(f"Error retrieving survey result: {e}")
        return None

def prepare_data_for_prediction(data):
    """Prepare the survey data for model prediction"""

    # Create a DataFrame with the expected column order
    feature_order = [
        'HighBP', 'HighChol', 'CholCheck',
        'BMI', 'Smoker', 'Stroke', 'HeartDiseaseorAttack', 'PhysActivity',
        'Fruits', 'Veggies', 'HvyAlcoholConsump',
        'AnyHealthcare', 'NoDocbcCost', 'GenHlth',
        'MentHlth', 'PhysHlth', 'DiffWalk',
        'Sex', 'Age', 'Education', 'Income'
    ]
    
    # Create DataFrame with ordered features
    df = pd.DataFrame([{key: data[key] for key in feature_order}])

    st_conn = st.connection('gcs', type=FilesConnection)
    with st_conn.open(
        'streamlit-bucket-tq/my_scaler.pkl', 
        'rb') as model_file:
        scaler = pickle.load(model_file)

    # Transform the test data using the same scaler
    
    df = scaler.transform(df)
    
    return df


def predict_diabetes_risk(data, model):
    """Make diabetes prediction using the model"""
    try:
        # Prepare the data
        X = prepare_data_for_prediction(data)
        if X is None:
            return None
        
        # Make prediction
        prediction = model.predict(X)
        probability = model.predict_proba(X)[0]
        
        return {
            'prediction': prediction[0],
            'probability': probability[1]  # Probability of having diabetes
        }
    except Exception as e:
        st.error(f"Error making prediction: {e}")
        st.error(f"Model type: {type(model)}")
        return None


def display_prediction_results(prediction_result):
    """Display the prediction results with a user-friendly interface"""
    st.markdown("## Your Diabetes Risk Assessment")
    
    # Calculate risk level
    probability = prediction_result['probability']
    if prediction_result['prediction'] >= 1:
        if probability > 0.7:
            risk_level = "High"
            color = "#ff4b4b"
            bg_color = "#fff3f3"
        else:
            risk_level = "Moderate"
            color = "#ffa500"
            bg_color = "#fff8f0"
    else:
        risk_level = "Low"
        color = "#00cc00"
        bg_color = "#f0fff0"

    # Display risk level box
    st.markdown(f"""
        <div style='
            background-color: {bg_color};
            padding: 20px;
            border-radius: 10px;
            border-left: 5px solid {color};
            margin-bottom: 20px;
        '>
            <h3 style='color: {color}; margin-top: 0;'>{risk_level} Risk Level</h3>
            <p style='font-size: 1.1em; margin-bottom: 10px;'>
                Your risk assessment indicates a {risk_level.lower()} risk for diabetes
            </p>
            <p style='font-size: 1.2em; font-weight: bold;'>
                Risk Probability: {probability:.1%}
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Display recommendations based on risk level
    st.markdown("### Recommended Actions")
    
    if prediction_result['prediction'] >= 1:
        st.markdown("""
        <div style='background-color: #f8f9fa; padding: 20px; border-radius: 10px;'>
            <h4 style='color: #1a1f36; margin-top: 0;'>Important Next Steps:</h4>
            <ol>
                <li style='margin-bottom: 10px;'><strong>Consult a Healthcare Provider</strong>
                    <ul>
                        <li>Schedule an appointment with your doctor</li>
                        <li>Get comprehensive blood sugar testing</li>
                        <li>Discuss your risk factors and management plan</li>
                    </ul>
                </li>
                <li style='margin-bottom: 10px;'><strong>Lifestyle Modifications</strong>
                    <ul>
                        <li>Follow a balanced, diabetes-friendly diet</li>
                        <li>Engage in regular physical activity (150 minutes/week)</li>
                        <li>Maintain a healthy weight</li>
                    </ul>
                </li>
                <li style='margin-bottom: 10px;'><strong>Regular Monitoring</strong>
                    <ul>
                        <li>Monitor blood sugar levels as recommended</li>
                        <li>Track blood pressure and cholesterol</li>
                        <li>Keep a log of your health metrics</li>
                    </ul>
                </li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='background-color: #f8f9fa; padding: 20px; border-radius: 10px;'>
            <h4 style='color: #1a1f36; margin-top: 0;'>Maintaining Good Health:</h4>
            <ol>
                <li style='margin-bottom: 10px;'><strong>Preventive Care</strong>
                    <ul>
                        <li>Schedule regular check-ups</li>
                        <li>Get routine blood sugar screenings</li>
                        <li>Monitor your blood pressure</li>
                    </ul>
                </li>
                <li style='margin-bottom: 10px;'><strong>Healthy Lifestyle</strong>
                    <ul>
                        <li>Maintain a balanced diet</li>
                        <li>Regular exercise routine</li>
                        <li>Adequate sleep and stress management</li>
                    </ul>
                </li>
                <li style='margin-bottom: 10px;'><strong>Risk Awareness</strong>
                    <ul>
                        <li>Learn about diabetes symptoms</li>
                        <li>Stay informed about prevention strategies</li>
                        <li>Regular health screenings</li>
                    </ul>
                </li>
            </ol>
        </div>
        """, unsafe_allow_html=True)

def hash_password(password):
    return generate_password_hash(password, method='pbkdf2:sha256')

def verify_password(password, hash_):
    return check_password_hash(hash_, password)

def create_hcp(conn, email, password, full_name, license_number):
    cur = conn.cursor()
    try:
        password_hash = hash_password(password)
        cur.execute(
            "INSERT INTO hcps (email, password_hash, full_name, license_number) VALUES (%s, %s, %s, %s)",
            (email, password_hash, full_name, license_number)
        )
        conn.commit()
        return True
    except psycopg2.Error as e:
        st.error(f"Error creating HCP account: {e}")
        return False

def authenticate_hcp(conn, email, password):
    cur = conn.cursor()
    cur.execute("SELECT password_hash, full_name FROM hcps WHERE email = %s", (email,))
    result = cur.fetchone()
    
    if result and verify_password(password, result[0]):
        return {"full_name": result[1]}
    return None

def add_home_button():
    """Add a smaller back to home button at the top of the page"""
    col1, col2, col3 = st.columns([0.6, 4.4, 1])
    with col1:
        if st.button("← Back", key="home_button"):
            st.session_state.current_page = "home"
            st.session_state.user_name = None
            st.session_state.authenticated = False
            st.rerun()
    st.markdown("""
        <style>
            /* Back button styling */
            div[data-testid="column"]:first-child .stButton > button {
                width: 100%;
                background-color: transparent;
                color: #0066ff;
                border: 1px solid #0066ff;
                border-radius: 4px;
                padding: 0.25rem 0.5rem;  /* Reduced padding */
                font-size: 0.85rem;  /* Smaller font size */
                min-height: 0px;  /* Remove minimum height */
                height: auto;  /* Adjust height automatically */
            }
            
            div[data-testid="column"]:first-child .stButton > button:hover {
                background-color: #f0f7ff;
                border-color: #0052cc;
                color: #0052cc;
            }
        </style>
    """, unsafe_allow_html=True)
    st.divider()



def show_home():
    # Main title and subtitle
    st.markdown('<h1 class="main-title">Welcome to Diabetes Information Portal</h1>', unsafe_allow_html=True)
    st.markdown("""
        <p class="subtitle">Your trusted resource for diabetes information and risk<br>
        assessment. Choose your path below to get started on your<br>
        health journey.</p>
    """, unsafe_allow_html=True)

    # Create two columns for the cards
    col1, spacer, col2 = st.columns([1, 0.1, 1])

    with col1:
        st.markdown("""
            <div class="card">
                <h2 class="card-title">Healthcare Professional</h2>
                <p class="card-text">Access professional medical information, patient data, and clinical resources.</p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Access HCP Portal", use_container_width=True):
            st.session_state.current_page = "hcp_auth"
            st.rerun()

    with col2:
        st.markdown("""
            <div class="card">
                <h2 class="card-title">Individual User</h2>
                <p class="card-text">Take a risk assessment survey or view educational resources about diabetes.</p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Start Your Journey", use_container_width=True):
            st.session_state.current_page = "journey_options"
            st.rerun()

def show_hcp_auth():
    add_home_button()
    st.markdown('<h1 style="text-align: center;">Healthcare Professional Portal</h1>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        with st.form("login_form"):
            st.subheader("Login")
            login_email = st.text_input("Email")
            login_password = st.text_input("Password", type="password")
            login_submitted = st.form_submit_button("Login")
            
            if login_submitted:
                conn = init_db()
                auth_result = authenticate_hcp(conn, login_email, login_password)
                if auth_result:
                    st.session_state.authenticated = True
                    st.session_state.user_name = auth_result["full_name"]
                    st.rerun()
                else:
                    st.error("Invalid credentials")
    
    with tab2:
        with st.form("signup_form"):
            st.subheader("Sign Up")
            full_name = st.text_input("Full Name*")
            email = st.text_input("Email*")
            password = st.text_input("Password*", type="password")
            license_number = st.text_input("License Number*")
            signup_submitted = st.form_submit_button("Sign Up")
            
            if signup_submitted:
                if all([email, password, full_name, license_number]):
                    conn = init_db()
                    if create_hcp(conn, email, password, full_name, license_number):
                        st.success("Account created successfully! Please login.")
                else:
                    st.error("All fields are required.")

def save_survey_results(conn, survey_data):
    """Save survey results to database"""
    cur = conn.cursor()
    try:
        # Convert categorical responses to numeric values
        numeric_data = convert_survey_responses(survey_data)
        
        cur.execute('''
            INSERT INTO survey_results (
                high_blood_pressure, high_cholesterol, cholesterol_check, 
                bmi, smoking, stroke, heart_disease, physical_activity,
                fruit_consumption, vegetable_consumption, heavy_drinker,
                healthcare_coverage, doctor_cost_barrier, general_health,
                mental_health, physical_health, difficulty_walking,
                gender, age, education, income
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s
            )
        ''', (
            numeric_data['high_bp'],
            numeric_data['high_chol'],
            numeric_data['chol_check'],
            numeric_data['bmi'],
            numeric_data['smoking'],
            numeric_data['stroke'],
            numeric_data['heart_disease'],
            numeric_data['physical_activity'],
            numeric_data['fruit_consumption'],
            numeric_data['vegetable_consumption'],
            numeric_data['heavy_drinker'],
            numeric_data['healthcare_coverage'],
            numeric_data['doctor_cost_barrier'],
            numeric_data['general_health'],
            numeric_data['mental_health'],
            numeric_data['physical_health'],
            numeric_data['difficulty_walking'],
            numeric_data['gender'],
            numeric_data['age'],
            numeric_data['education'],
            numeric_data['income']
        ))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error saving survey results: {e}")
        return False

def convert_survey_responses(survey_data):
    """Convert categorical responses to numeric values"""
    
    # Conversion dictionaries
    yes_no_mapping = {
        "Yes": 1,
        "No": 0,
        "": None
    }
    
    general_health_mapping = {
        "Excellent": 1,
        "Very Good": 2,
        "Good": 3,
        "Fair": 4,
        "Poor": 5,
        "": None
    }
    
    gender_mapping = {
        "Male": 1,
        "Female": 2,
        "Other": 3,
        "": None
    }
    
    education_mapping = {
        "Never attended school or only kindergarten": 1,
        "Grades 1 through 8 (Elementary)": 2,
        "Grades 9 through 11 (Some high school)": 3,
        "Grade 12 or GED (High school graduate)": 4,
        "College 1 year to 3 years (Some college or technical school)": 5,
        "College 4 years or more (College graduate)": 6,
        "": None
    }
    
    income_mapping = {
        "Less than $10,000": 1,
        "Less than $15,000": 2,
        "Less than $20,000": 3,
        "Less than $25,000": 4,
        "Less than $35,000": 5,
        "Less than $50,000": 6,
        "Less than $75,000": 7,
        "$75,000 or more": 8,
        "": None
    }
    
    # Convert the data
    converted_data = {
        'high_bp': yes_no_mapping[survey_data['high_bp']],
        'high_chol': yes_no_mapping[survey_data['high_chol']],
        'chol_check': yes_no_mapping[survey_data['chol_check']],
        'bmi': float(survey_data['bmi']) if survey_data['bmi'] is not None else None,
        'smoking': yes_no_mapping[survey_data['smoking']],
        'stroke': yes_no_mapping[survey_data['stroke']],
        'heart_disease': yes_no_mapping[survey_data['heart_disease']],
        'physical_activity': yes_no_mapping[survey_data['physical_activity']],
        'fruit_consumption': yes_no_mapping[survey_data['fruit_consumption']],
        'vegetable_consumption': yes_no_mapping[survey_data['vegetable_consumption']],
        'heavy_drinker': yes_no_mapping[survey_data['heavy_drinker']],
        'healthcare_coverage': yes_no_mapping[survey_data['healthcare_coverage']],
        'doctor_cost_barrier': yes_no_mapping[survey_data['doctor_cost_barrier']],
        'general_health': general_health_mapping[survey_data['general_health']],
        'mental_health': survey_data['mental_health'],
        'physical_health': survey_data['physical_health'],
        'difficulty_walking': yes_no_mapping[survey_data['difficulty_walking']],
        'gender': gender_mapping[survey_data['gender']],
        'age': survey_data['age'],
        'education': education_mapping[survey_data['education']],
        'income': income_mapping[survey_data['income']]
    }
    
    return converted_data
    
def show_diabetes_risk_survey():
    add_home_button()
    st.markdown('<h1 style="text-align: center;">Diabetes Risk Assessment Survey</h1>', unsafe_allow_html=True)

    # Initialize database connection
    conn = init_db()
    
    with st.form("diabetes_risk_survey"):
        st.markdown('<div class="survey-section">', unsafe_allow_html=True)
        st.subheader("Medical History")
        high_bp = st.radio("Do you have high blood pressure?", options=["", "Yes", "No"])
        high_chol = st.radio("Do you have high cholesterol?", options=["", "Yes", "No"])
        chol_check = st.radio("Have you had cholesterol check in 5 years?", options=["", "Yes", "No"])
        bmi = st.number_input("What is your BMI (Body Mass Index)?", min_value=10.0, max_value=50.0, value=None)
        smoking = st.radio("Have you smoked at least 100 cigarettes in your entire life?", options=["", "Yes", "No"])
        stroke = st.radio("Have you had a stroke?", options=["", "Yes", "No"])
        heart_disease = st.radio("Have you had coronary heart disease (CHD) or myocardial infarction (MI)?", options=["", "Yes", "No"])
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="survey-section">', unsafe_allow_html=True)
        st.subheader("Lifestyle & Health")
        physical_activity = st.radio("Have you had physical activity in past 30 days - not including job?", options=["", "Yes", "No"])
        fruit_consumption = st.radio("Do you consume Fruit 1 or more times per day?", options=["", "Yes", "No"])
        vegetable_consumption = st.radio("Do you consume Vegetables 1 or more times per day?", options=["", "Yes", "No"])
        heavy_drinker = st.radio("Are you a heavy drinker? (adult men having more than 14 drinks per week and adult women having more than 7 drinks per week)", options=["", "Yes", "No"])
        healthcare_coverage = st.radio("Do you have any kind of health care coverage, including health insurance, prepaid plans such as HMO, etc.?", options=["", "Yes", "No"])
        doctor_cost_barrier = st.radio("Was there a time in the past 12 months when you needed to see a doctor but could not because of cost?", options=["", "Yes", "No"])
        general_health = st.radio(
            "Would you say that in general your health is:",
            options=["", "Excellent", "Very Good", "Good", "Fair", "Poor"]
        )
        mental_health = st.number_input(
            "Now thinking about your mental health, which includes stress, depression, and problems with emotions, for how many days during the past 30 days was your mental health not good?",
            min_value=0, max_value=30, value=None
        )
        physical_health = st.number_input(
            "Now thinking about your physical health, which includes physical illness and injury, for how many days during the past 30 days was your physical health not good?",
            min_value=0, max_value=30, value=None
        )
        difficulty_walking = st.radio("Do you have serious difficulty walking or climbing stairs?", options=["", "Yes", "No"])
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="survey-section">', unsafe_allow_html=True)
        st.subheader("Demographics")
        gender = st.radio("What is your gender?", options=["", "Male", "Female", "Other"])
        age = st.number_input("What is your age?", min_value=18, max_value=120, value=None)
        education = st.radio(
            "What is your education level?",
            options=[
                "",
                "Never attended school or only kindergarten",
                "Grades 1 through 8 (Elementary)",
                "Grades 9 through 11 (Some high school)",
                "Grade 12 or GED (High school graduate)",
                "College 1 year to 3 years (Some college or technical school)",
                "College 4 years or more (College graduate)"
            ]
        )
        income = st.radio(
            "What is your Income level?",
            options=[
                "",
                "Less than $10,000",
                "Less than $15,000",
                "Less than $20,000",
                "Less than $25,000",
                "Less than $35,000",
                "Less than $50,000",
                "Less than $75,000",
                "$75,000 or more"
            ]
        )
        st.markdown('</div>', unsafe_allow_html=True)

        submitted = st.form_submit_button("Submit Survey")
        
    if submitted:
        # Create a dictionary of survey responses
        survey_data = {
            'high_bp': high_bp,
            'high_chol': high_chol,
            'chol_check': chol_check,
            'bmi': bmi,
            'smoking': smoking,
            'stroke': stroke,
            'heart_disease': heart_disease,
            'physical_activity': physical_activity,
            'fruit_consumption': fruit_consumption,
            'vegetable_consumption': vegetable_consumption,
            'heavy_drinker': heavy_drinker,
            'healthcare_coverage': healthcare_coverage,
            'doctor_cost_barrier': doctor_cost_barrier,
            'general_health': general_health,
            'mental_health': mental_health,
            'physical_health': physical_health,
            'difficulty_walking': difficulty_walking,
            'gender': gender,
            'age': age,
            'education': education,
            'income': income
        }
        
        # Check for empty responses
        empty_fields = [field for field, value in survey_data.items() if value == "" or value is None]
        
        if empty_fields:
            st.error("Please answer all questions before submitting.")
        else:
            # Save to database
            if save_survey_results(conn, survey_data):
                st.success("Thank you for completing the survey! Your responses have been saved.")
                
                # Load model and make prediction
                model = load_ml_model()
                if model:
                    # Get latest survey result
                    latest_result = get_latest_survey_result(conn)
                    if latest_result:
                        # Make prediction
                        prediction_result = predict_diabetes_risk(latest_result, model)
                        if prediction_result:
                            # Display prediction results
                            display_prediction_results(prediction_result)
                            
                            # Navigation button
                            if st.button("Return to Journey Options"):
                                st.session_state.current_page = "journey_options"
                                st.rerun()
                else:
                    st.error("Unable to load the prediction model. Please try again later.")

def show_diabetes_information():
    add_home_button()
    st.markdown('<h1 style="text-align: center;">Diabetes Information</h1>', unsafe_allow_html=True)
    st.write("Learn more about diabetes, its causes, symptoms, and prevention.")
    # Display visualization if "View Information" was clicked
    # if st.session_state.get("current_page") == "info":

    # st.markdown('<div class="card">', unsafe_allow_html=True)
    st.write("Content about diabetes will be displayed here.")
    run_patient_visulization()  # Call the visualization function from visulization_patient.py
    # st.markdown('</div>', unsafe_allow_html=True)
    
    if st.button("Back to Journey Options"):
        st.session_state.current_page = "journey_options"
        st.rerun()

def show_journey_options():
    add_home_button()
    st.markdown("""
        <h1 style='text-align: center;'>Your Journey Options</h1>
        <p style='text-align: center; font-size: 1.2rem; color: #666; margin-bottom: 2rem;'>
            Choose your path to learn more about diabetes
        </p>
    """, unsafe_allow_html=True)
    
    col1, spacer, col2 = st.columns([1, 0.1, 1])
    
    with col1:
        st.markdown("""
            <div class="card">
                <h2 class="card-title">Take Risk Survey</h2>
                <p class="card-text">Complete a quick assessment to understand your diabetes risk factors.</p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Start Survey", use_container_width=True):
            st.session_state.current_page = "survey"
            st.rerun()

    with col2:
        st.markdown("""
            <div class="card">
                <h2 class="card-title">Learn About Diabetes</h2>
                <p class="card-text">Access comprehensive information about diabetes management and prevention.</p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("View Information", use_container_width=True):
            st.session_state.current_page = "info"
            st.rerun()


def show_population_dashboard():
    st.markdown("<h1 style='text-align: center;'>Population Level Dashboard</h1>", unsafe_allow_html=True)
    run_pcp_visulization()
    

def show_individual_dashboard():
    st.markdown("<h1 style='text-align: center;'>Individual Level Dashboard</h1>", unsafe_allow_html=True)
    run_real_patient_visulization(st.session_state.user_name)
    
    
    

def show_hcp_dashboard():
    add_home_button()
    st.markdown(f"""
        <h1 style='text-align: center;'>HCP Dashboard</h1>
        <p style='text-align: center; color: #666;'>Welcome, Dr. {st.session_state.user_name}</p>
            Choose the information about patients you want to view
        </p>
    """, unsafe_allow_html=True)
    
    col1, spacer, col2 = st.columns([1, 0.1, 1])
    
    with col1:
        st.markdown("""
            <div class="card">
                <h2 class="card-title">Population Level Dashboard</h2>
                <p class="card-text">This section provides insights into patient demographics and test results at a population level using publicly available data.</p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("View Population Information", use_container_width=True):
            st.session_state.current_page = "pcp_visulization"
            st.rerun()

    with col2:
        st.markdown("""
            <div class="card">
                <h2 class="card-title">Individual Level Dashboard</h2>
                <p class="card-text">This section provides insights into your patient basic information using existing patient information.</p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("View Each Patient Information", use_container_width=True):
            st.session_state.current_page = "real_patient_visulization"
            st.rerun()
    
    # Add logout button
    col1, col2, col3 = st.columns([6, 2, 2])
    with col3:
        if st.button("Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user_name = None
            st.session_state.current_page = "home"
            st.rerun()
    

def main():
    st.set_page_config(
        page_title="Diabetes Information Portal",
        page_icon="🏥",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    # Apply custom styles
    apply_custom_styles()

    # Initialize session states
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.user_name = None
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "home"

    # Navigation logic
    if st.session_state.authenticated:
        show_hcp_dashboard()
        if st.session_state.current_page == "pcp_visulization":
            show_population_dashboard()
        elif st.session_state.current_page == "real_patient_visulization":
            show_individual_dashboard()
    else:
        if st.session_state.current_page == "home":
            show_home()
        elif st.session_state.current_page == "hcp_auth":
            show_hcp_auth()
        elif st.session_state.current_page == "journey_options":
            show_journey_options()
        elif st.session_state.current_page == "survey":
            show_diabetes_risk_survey()
        elif st.session_state.current_page == "info":
            show_diabetes_information()

if __name__ == "__main__":
    main()
