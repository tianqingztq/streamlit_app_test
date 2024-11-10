import streamlit as st
import psycopg2
from werkzeug.security import generate_password_hash, check_password_hash
import os
from visualization.visulization_patient import run_patient_visulization
from visualization.visulization_pcp import run_pcp_visulization

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
    conn.commit()
    return conn

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

def show_diabetes_risk_survey():
    add_home_button()
    st.markdown('<h1 style="text-align: center;">Diabetes Risk Assessment Survey</h1>', unsafe_allow_html=True)
    
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
        general_health = st.select_slider(
            "Would you say that in general your health is:",
            options=["", "Excellent", "Very Good", "Good", "Fair", "Poor"],
            value=""
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
        education = st.select_slider(
            "What is your education level?",
            options=[
                "",
                "Never attended school or only kindergarten",
                "Grades 1 through 8 (Elementary)",
                "Grades 9 through 11 (Some high school)",
                "Grade 12 or GED (High school graduate)",
                "College 1 year to 3 years (Some college or technical school)",
                "College 4 years or more (College graduate)"
            ],
            value=""
        )
        income = st.select_slider(
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
            ],
            value=""
        )
        st.markdown('</div>', unsafe_allow_html=True)

        submitted = st.form_submit_button("Submit Survey")
        
        if submitted:
            # Validate that all questions are answered
            all_fields = [high_bp, high_chol, chol_check, bmi, smoking, stroke, heart_disease,
                         physical_activity, fruit_consumption, vegetable_consumption, heavy_drinker,
                         healthcare_coverage, doctor_cost_barrier, general_health, mental_health,
                         physical_health, difficulty_walking, gender, age, education, income]
            
            if "" in all_fields or None in all_fields:
                st.error("Please answer all questions before submitting.")
            else:
                st.success("Thank you for completing the survey!")
                st.write("Based on your responses, we recommend discussing your risk factors with a healthcare provider.")
                if st.button("Return to Journey Options"):
                    st.session_state.current_page = "journey_options"
                    st.rerun()

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

def show_hcp_dashboard():
    add_home_button()
    st.markdown(f"""
        <h1 style='text-align: center;'>HCP Dashboard</h1>
        <p style='text-align: center; color: #666;'>Welcome, Dr. {st.session_state.user_name}</p>
    """, unsafe_allow_html=True)
    
    # run pcp visulization information
    run_pcp_visulization()
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