import streamlit as st

st.write("Secrets loaded:", st.secrets["CRO_API"])
st.write("Email:", st.secrets["CRO_API"]["email"])
st.write("API Key:", st.secrets["CRO_API"]["api_key"])
