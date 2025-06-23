import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
import io
import chromedriver_autoinstaller

# Auto-install matching chromedriver version
chromedriver_autoinstaller.install()

def get_entity_name(entity_number, driver):
    try:
        driver.get("https://core.cro.ie/search")

        # Wait for the search field to appear
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "search-field"))
        )

        search_input = driver.find_element(By.ID, "search-field")
        search_input.clear()
        search_input.send_keys(entity_number)
        search_input.send_keys(Keys.RETURN)

        # Wait for results to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".result-body .company-name"))
        )

        name_element = driver.find_element(By.CSS_SELECTOR, ".result-body .company-name")
        return name_element.text.strip()
    except Exception:
        return "N/A"

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    return webdriver.Chrome(options=chrome_options)

def main():
    st.set_page_config(page_title="CRO Entity Lookup")
    st.title("🔍 CRO Entity Number Lookup")
    st.write("Enter entity numbers manually or upload a CSV file to fetch company names from [core.cro.ie](https://core.cro.ie/search).")

    input_method = st.radio("Choose input method:", ("Manual Input", "Upload CSV"))

    entity_numbers = []

    if input_method == "Manual Input":
        entity_input = st.text_area("Enter Entity Numbers (one per line)", height=200)
        if entity_input:
            entity_numbers = [line.strip() for line in entity_input.splitlines() if line.strip()]
    else:
        uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])
        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)
            entity_col = st.selectbox("Select column with entity numbers", df.columns)
            entity_numbers = df[entity_col].dropna().astype(str).tolist()

    if st.button("Search") and entity_numbers:
        st.info(f"Processing {len(entity_numbers)} entity number(s)...")
        with st.spinner("Searching the CRO site..."):
            driver = setup_driver()
            results = []
            for number in entity_numbers:
                name = get_entity_name(number, driver)
                results.append({"Entity Number": number, "Entity Name": name})
            driver.quit()

        results_df = pd.DataFrame(results)
        st.success("Search completed!")
        st.subheader("📋 Results")
        st.dataframe(results_df)

        # CSV download
        csv = results_df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Download Results as CSV", csv, "entity_results.csv", "text/csv")
    elif st.button("Search") and not entity_numbers:
        st.warning("Please provide at least one entity number.")

if __name__ == "__main__":
    main()
