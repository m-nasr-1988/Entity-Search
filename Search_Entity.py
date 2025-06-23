import streamlit as st
import pandas as pd
import requests

API_URL = "https://services.cro.ie/cws/companies"

def lookup_entity(entity_number: str) -> str:
    """
    Query CRO Open Services for a single company number.
    Returns the company/business name or 'N/A'.
    """
    params = {
        "company_num": entity_number,
        "company_bus_ind": "E",      # C = companies, B = business names, E = either
        "max": 1,                    # only need the first (exact) match
        "format": "json"
    }
    try:
        resp = requests.get(API_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()           # returns a list of Company objects
        if data:
            return data[0].get("company_name", "N/A")
    except Exception as e:
        st.warning(f"{entity_number}: {e}")
    return "N/A"

# ───────────────────────────── Streamlit UI ───────────────────────────── #
st.set_page_config(page_title="CRO Entity Lookup")
st.title("🔎 CRO Entity Number → Name")

st.markdown(
    "Paste **one or many** CRO entity numbers. "
    "Separate them with commas, spaces, or new lines."
)

raw_input = st.text_area("Entity numbers", height=160)

if st.button("Search"):
    # normalise separators → commas, then split & dedupe
    numbers = {
        n.strip()
        for n in raw_input.replace("\n", ",").replace(" ", ",").split(",")
        if n.strip()
    }

    if not numbers:
        st.error("Please enter at least one entity number.")
    else:
        with st.spinner("Contacting CRO…"):
            results = [{"Entity Number": n, "Entity Name": lookup_entity(n)}
                       for n in sorted(numbers)]

        df = pd.DataFrame(results)
        st.success("Done!")
        st.dataframe(df, use_container_width=True)

        # download button
        csv = df.to_csv(index=False).encode()
        st.download_button("📥 Download CSV", csv, "cro_entities.csv", "text/csv")
