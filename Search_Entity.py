import streamlit as st
import requests
import base64
import pandas as pd
import io

st.set_page_config(page_title="CRO Lookup Tool", layout="wide")

st.title("CRO Entity Number Lookup")
st.write("Enter CRO entity numbers manually or upload a CSV file with a 'registration_number' column.")

# Option to input manually or upload CSV
input_method = st.radio("Choose Input Method:", ("Manual Input", "Upload CSV"))

entities = []

if input_method == "Manual Input":
    entity_input = st.text_area("Entity Numbers", height=150, placeholder="E.g. 691054, 123456")
    if entity_input:
        entities = [e.strip() for e in entity_input.replace(",", "\n").split("\n") if e.strip()]
else:
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
    if uploaded_file is not None:
        df_uploaded = pd.read_csv(uploaded_file)
        if 'registration_number' not in df_uploaded.columns:
            st.error("CSV must contain a 'registration_number' column")
        else:
            entities = df_uploaded['registration_number'].astype(str).tolist()

if st.button("Search", key="search_button_1") and entities:
    try:
        email = st.secrets["CRO_API"]["email"]
        api_key = st.secrets["CRO_API"]["api_key"]
    except KeyError:
        st.error("Missing API credentials in secrets.toml file.")
        st.stop()

    credentials = f"{email}:{api_key}"
    encoded_credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")
    headers = {"Authorization": f"Basic {encoded_credentials}"}

    results_data = []
    progress_bar = st.progress(0)

    for i, entity in enumerate(entities):
        try:
            url = f"https://services.cro.ie/cws/companies?company_num={entity}&company_bus_ind=E&max=1&format=json"
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data and isinstance(data, list) and "company_name" in data[0]:
                    row = data[0]
                    row["searched_entity"] = entity
                    results_data.append(row)
                else:
                    results_data.append({"searched_entity": entity, "error": "No company data found."})
            else:
                results_data.append({"searched_entity": entity, "error": f"HTTP {response.status_code}"})
        except Exception as e:
            results_data.append({"searched_entity": entity, "error": str(e)})

        progress_bar.progress((i + 1) / len(entities))

    progress_bar.empty()

    df_results = pd.DataFrame(results_data)

    st.subheader("Company Details Table")
    st.dataframe(df_results, use_container_width=True)

    csv_export = df_results.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download Results as CSV",
        data=csv_export,
        file_name="cro_lookup_results.csv",
        mime="text/csv"
    )

elif st.button("Search", key="search_button_2"):
    st.warning("Please enter or upload at least one entity number.")
