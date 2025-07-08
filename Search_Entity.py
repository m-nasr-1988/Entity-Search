import streamlit as st
import requests
import base64

st.title("CRO Entity Number Lookup")

st.write("Enter CRO entity numbers separated by commas or new lines.")

entity_input = st.text_area("Entity Numbers", height=150, placeholder="E.g. 691054, 123456")

if st.button("Search"):
    if not entity_input.strip():
        st.warning("Please enter at least one entity number.")
    else:
        # Parse input into list of entity numbers
        entities = [e.strip() for e in entity_input.replace(",", "\n").split("\n") if e.strip()]
        
        # Load credentials from secrets.toml
        try:
            email = st.secrets["CRO_API"]["email"]
            api_key = st.secrets["CRO_API"]["api_key"]
        except KeyError:
            st.error("Missing API credentials in secrets.toml file.")
            st.stop()

        # Encode email:api_key in base64 for Authorization header
        credentials = f"{email}:{api_key}"
        encoded_credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")
        headers = {
            "Authorization": f"Basic {encoded_credentials}"
        }

        results = {}

        for entity in entities:
            try:
                url = f"https://services.cro.ie/cws/companies?company_num={entity}&company_bus_ind=E&max=1&format=json"
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if data and isinstance(data, list) and "company_name" in data[0]:
                        results[entity] = data[0]["company_name"]
                    else:
                        results[entity] = "N/A"
                else:
                    results[entity] = f"Error: {response.status_code} — {response.reason}"
            except Exception as e:
                results[entity] = f"Exception: {e}"

        st.subheader("Results")
        for entity, name in results.items():
            st.write(f"**{entity}**: {name}")
