# streamlit_app.py

import streamlit as st
from st_files_connection import FilesConnection
import pickle

# Create connection object and retrieve file contents.
conn = st.connection('gcs', type=FilesConnection)
with conn.open('streamlit-bucket-tq/rf_model.pkl', 'rb') as file:
    rf_model = pickle.load(file)
#rfmodel = conn.read("streamlit-bucket-tq/rf_model.pkl", ttl=600) # cache the result for 600 seconds.
#rf_model = pickle.load(rfmodel)
st.write(rf_model)
