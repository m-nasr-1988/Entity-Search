import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import time
import tempfile
import os

def get_entity_name(entity_number, driver):
    try:
        driver.get("https://core.cro.ie/search")
        time.sleep(3)

        search_input = driver.find_element(By.ID, "search-field")
        search_input.clear()
        search_input.send_keys(entity_number)
        search_input.send_keys(Keys.RETURN)

        time.sleep(3)

        name_element = driver.find_element(By.CSS_SELECTOR, ".result-body .company-name")
        return name_element.text.strip()
    except Exception:
        return "N/A"

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    return webdriver.Chrome(options=chrome_options)

def main():
    st.set_page_config(page_title="CRO Entity Name Lookup")
    st.title("CRO Entity Number → Name Lookup")

    entity_input = st.text_area("Enter Entity Numbers (one per line)", height=200)

    if st.button("Search"):
        entity_numbers = [line.strip() for line in entity_input.splitlines() if line.strip()]
        if not entity_numbers:
            st.warning("Please enter at least one entity number.")
            return

        with st.spinner("Searching..."):
            driver = setup_driver()
            results = {}
            for number in entity_numbers:
                results[number] = get_entity_name(number, driver)
            driver.quit()

        st.success("Search complete.")
        st.subheader("Results")
        st.table([{"Entity Number": k, "Entity Name": v} for k, v in results.items()])

if __name__ == "__main__":
    main()
