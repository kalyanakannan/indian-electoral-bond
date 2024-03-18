import pandas as pd
import streamlit as st
# from streamlit_gsheets import GSheetsConnection


def load_and_prepare_data(csv_file):
    """
    Loads company data from a CSV file, preprocesses it by renaming columns, standardizing company names,
    converting amount strings to integers, parsing dates, extracting years, and standardizing text case.

    Parameters:
    - csv_file: Path to the CSV file containing company data.

    Returns:
    - DataFrame with preprocessed company data.
    """
    # Load data from CSV
    # conn = st.connection("gsheets", type=GSheetsConnection)
    # df = conn.read(
    #     worksheet="Donors-list",
    #     ttl="10m",
    # )
    companies = pd.read_csv(csv_file)

    # Rename columns for clarity and consistency
    companies = companies.rename(columns={"Date of Purchase": "Date"})

    # Standardize company names using regular expressions for flexibility
    company_replacements = {
        r"FUTURE GAMING AND HOTEL SERVICES.*": "FUTURE GAMING AND HOTEL SERVICES PRIVATE LTD",
        r"AASHMAN ENERGY.*": "AASHMAN ENERGY PRIVATE LIMITED",
        r"APCO INFRATECH.*": "APCO INFRATECH PRIVATE LIMITED",
        r"MEGHA ENGINEERING.*": "MEGHA ENGINEERING AND INFRASTRUCTURES LIMITED",
    }
    for pattern, replacement in company_replacements.items():
        companies["Company"] = companies["Company"].str.replace(
            pattern, replacement, regex=True
        )

    # Convert amount strings to integers
    companies["Amount"] = (
        companies["Amount"].str.replace(",", "").astype(float).astype("int64")
    )

    # Parse dates and extract year
    companies["Date_format"] = pd.to_datetime(companies["Date"], format="%d/%b/%Y")
    companies["Year"] = companies["Date_format"].dt.year

    # Standardize case for 'Category' and 'Parent Company'
    companies["Category"] = companies["Category"].str.title()
    companies["Parent Company"] = companies["Parent Company"].str.title()

    return companies


def load_and_prepare_party_data(csv_file):
    # Load the dataset from a CSV file into a pandas DataFrame.
    parties = pd.read_csv(csv_file)

    # Initial regex replacements are commented out, but this code can be
    # used to standardize company names or correct frequent misspellings.
    # replacements = {
    #     r'FUTURE GAMING AND HOTEL SERVICES.*': 'FUTURE GAMING AND HOTEL SERVICES PRIVATE LTD',
    #     r'AASHMAN ENERGY.*': 'AASHMAN ENERGY PRIVATE LIMITED',
    #     r'APCO INFRATECH.*': 'APCO INFRATECH PRIVATE LIMITED'
    # }
    # Apply replacements to the 'Company' column using regex patterns.
    # for pattern, replacement in replacements.items():
    #     parties['Company'] = parties['Company'].str.replace(pattern, replacement, regex=True)

    # Clean the 'Amount' column by removing commas, converting to float for any potential
    # decimal amounts, and then converting to int64 to ensure a uniform numeric type.
    parties["Amount"] = (
        parties["Amount"].str.replace(",", "").astype(float).astype("int64")
    )

    # Convert the 'Date' column to a DateTime format for easier manipulation.
    # This assumes dates are in the 'day/month/Year' format.
    parties["Date_format"] = pd.to_datetime(parties["Date"], format="%d/%b/%Y")

    # Extract the year from the newly formatted 'Date_format' column for
    # potential time-based analyses or aggregations.
    parties["Year"] = parties["Date_format"].dt.year

    # Return the cleaned and prepared DataFrame for further processing.
    return parties
