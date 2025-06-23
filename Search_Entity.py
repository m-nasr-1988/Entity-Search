import streamlit as st
import requests
import base64

st.title("CRO Entity Name Finder")

# Instructions
st.markdown("Enter one or more entity numbers (comma-separated).")

# Input box
input_text = st.text_area("Entity Numbers", "691054, 602047")

# Button
if st.button("Search"):
    if input_text.strip() == "":
        st.warning("Please enter at least one entity number.")
    else:
        entity_numbers = [num.strip() for num in input_text.split(",") if num.strip()]
        
        # Read credentials from Streamlit secrets
        email = st.secrets["CRO_API"]["email"]
        api_key = st.secrets["CRO_API"]["api_key"]

        # Create Basic Auth header
        token = base64.b64encode(f"{email}:{api_key}".encode()).decode()
        headers = {"Authorization": f"Basic {token}"}

        results = {}

        for number in entity_numbers:
            try:
                params = {
                    "company_num": number,
                    "company_bus_ind": "E",
                    "max": 1,
                    "format": "json"
                }
                url = "https://services.cro.ie/cws/companies"
                response = requests.get(url, headers=headers, params=params, timeout=10)
                response.raise_for_status()

                data = response.json()
                name = data[0]["company_name"] if data else "N/A"
                results[number] = name
            except Exception as e:
                results[number] = f"Error: {e}"

        st.subheader("Results")
        for number, name in results.items():
            st.write(f"**{number}**: {name}")
