import streamlit as st
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
import time

# ---- Setup Headless Selenium Driver for Chromium on Streamlit Cloud ---- #
def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.binary_location = "/usr/bin/chromium"

    # Use Service object instead of deprecated executable_path
    service = Service(executable_path="/usr/bin/chromedriver")
    return webdriver.Chrome(service=service, options=chrome_options)

# ---- Function to Fetch Entity Name ---- #
def get_entity_name(entity_number):
    driver = setup_driver()
    try:
        driver.get("https://core.cro.ie/search")
        time.sleep(3)  # Let the page load

        # Locate the input box
        search_box = driver.find_element(By.ID, "mat-input-0")
        search_box.clear()
        search_box.send_keys(entity_number)
        search_box.send_keys(Keys.RETURN)
        time.sleep(5)  # Wait for results to load

        # Get entity name - you may need to adjust this selector
        results = driver.find_elements(By.CLASS_NAME, "search-result-name")

        if results:
            entity_name = results[0].text.strip()
        else:
            entity_name = "N/A"
    except Exception as e:
        st.error(f"Error while fetching entity {entity_number}: {e}")
        entity_name = "N/A"
    finally:
        driver.quit()

    return entity_name

# ---- Streamlit UI ---- #
st.set_page_config(page_title="CRO Entity Search", layout="centered")
st.title("🔎 CRO Entity Name Finder")
st.markdown("Enter one or more entity numbers separated by commas. The app will return the matching entity names or `N/A`.")

input_str = st.text_area("Enter Entity Numbers (comma-separated)", height=150)

if st.button("Search"):
    if input_str.strip():
        entity_numbers = [e.strip() for e in input_str.split(",") if e.strip()]
        result_data = []
        with st.spinner("Searching CRO..."):
            for entity in entity_numbers:
                name = get_entity_name(entity)
                result_data.append({"Entity Number": entity, "Entity Name": name})

        df = pd.DataFrame(result_data)
        st.success("Search complete.")
        st.dataframe(df)
    else:
        st.warning("Please enter at least one entity number.")
