import streamlit as st
import pandas as pd
import requests
import base64
import time

st.title("CRO Entity Lookup Tool")

upload_method = st.radio("Choose input method", ("Manual Entry", "Upload CSV"))

if upload_method == "Manual Entry":
    entity_input = st.text_area("Enter CRO Numbers (comma or newline-separated)", height=150)
    entity_numbers = [e.strip() for e in entity_input.replace(",", "\n").split("\n") if e.strip()]
else:
    uploaded_file = st.file_uploader("Upload CSV with column 'company_num'", type="csv")
    entity_numbers = []
    if uploaded_file:
        df_input = pd.read_csv(uploaded_file)
        if "company_num" in df_input.columns:
            entity_numbers = df_input["company_num"].astype(str).tolist()
        else:
            st.error("CSV must have a column named 'company_num'")

if st.button("Search", key="main_search_button") and entity_numbers:
    # Load credentials
    try:
        email = st.secrets["CRO_API"]["email"]
        api_key = st.secrets["CRO_API"]["api_key"]
    except KeyError:
        st.error("Missing CRO_API credentials in secrets.toml")
        st.stop()

    credentials = f"{email}:{api_key}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    headers = {"Authorization": f"Basic {encoded_credentials}"}

    result_data = []

    progress = st.progress(0)
    status_text = st.empty()

    for idx, entity in enumerate(entity_numbers):
        for ind_type in ['C', 'B']:
            url = f"https://services.cro.ie/cws/companies?company_num={entity}&company_bus_ind={ind_type}&format=json"
            try:
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if data:
                        for d in data:
                            if d.get("company_bus_ind") != ind_type:
                                continue
                            address = ", ".join(filter(None, [d.get(f"company_addr_{i}", "") for i in range(1, 5)]))
                            result_data.append({
                                "Entity Number": d.get("company_num", ""),
                                "Company Name": d.get("company_name", ""),
                                "Address": address,
                                "Status": d.get("company_status_desc", "").strip(),
                                "Type": d.get("comp_type_desc", ""),
                                "Place of Business": d.get("place_of_business", ""),
                                "Eircode": d.get("eircode", ""),
                                "Entity Type": "Company" if ind_type == "C" else "Business"
                            })
                    else:
                        result_data.append({
                            "Entity Number": entity,
                            "Company Name": "Not Found",
                            "Address": "",
                            "Status": "",
                            "Type": "",
                            "Place of Business": "",
                            "Eircode": "",
                            "Entity Type": "Company" if ind_type == "C" else "Business"
                        })
                else:
                    result_data.append({
                        "Entity Number": entity,
                        "Company Name": f"Error: {response.status_code}",
                        "Address": "",
                        "Status": "",
                        "Type": "",
                        "Place of Business": "",
                        "Eircode": "",
                        "Entity Type": "Company" if ind_type == "C" else "Business"
                    })
            except Exception as e:
                result_data.append({
                    "Entity Number": entity,
                    "Company Name": f"Exception: {e}",
                    "Address": "",
                    "Status": "",
                    "Type": "",
                    "Place of Business": "",
                    "Eircode": "",
                    "Entity Type": "Company" if ind_type == "C" else "Business"
                })

        progress.progress((idx + 1) / len(entity_numbers))
        status_text.text(f"Processed {idx + 1} of {len(entity_numbers)}")
    progress.empty()
    status_text.empty()

    df_result = pd.DataFrame(result_data)
    df_result.insert(0, "No.", range(1, len(df_result) + 1))  # Add new numbered column
    st.subheader("Results")
    st.dataframe(df_result, use_container_width=True, hide_index=True)

    csv = df_result.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download CSV", csv, file_name="cro_entity_results.csv", mime="text/csv")
