import streamlit as st
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Setup WebDriver
def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.binary_location = "/usr/bin/chromium"
    service = Service(executable_path="/usr/bin/chromedriver")
    return webdriver.Chrome(service=service, options=chrome_options)

# Function to fetch entity name from CRO
def get_entity_name(entity_number):
    driver = setup_driver()
    try:
        driver.get("https://core.cro.ie/search")

        # Wait for the input field to load
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Search for a company or business name"]'))
        )
        search_box.clear()
        search_box.send_keys(entity_number)
        search_box.send_keys(Keys.RETURN)

        # Wait for results to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "search-result-name"))
        )
        results = driver.find_elements(By.CLASS_NAME, "search-result-name")
        entity_name = results[0].text.strip() if results else "N/A"

    except Exception as e:
        st.warning(f"Error while fetching entity {entity_number}: {e}")
        entity_name = "N/A"
    finally:
        driver.quit()
    return entity_name

# Streamlit UI
st.title("CRO Entity Number Lookup")
st.markdown("Enter CRO entity numbers (comma-separated or newline-separated) below.")

input_str = st.text_area("Enter Entity Numbers", height=150)

if st.button("Search"):
    if input_str.strip():
        entity_numbers = [e.strip() for e in input_str.replace('\n', ',').split(',') if e.strip()]
        results = []

        with st.spinner("Searching..."):
            for entity in entity_numbers:
                name = get_entity_name(entity)
                results.append({"Entity Number": entity, "Entity Name": name})
        
        df = pd.DataFrame(results)
        st.success("Search completed.")
        st.dataframe(df, use_container_width=True)
    else:
        st.error("Please enter at least one entity number.")
