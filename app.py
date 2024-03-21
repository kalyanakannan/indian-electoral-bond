import streamlit as st
from data_loader import load_and_prepare_data, load_and_prepare_party_data
from news_handler import display_news
from party_handler import display_individual_party_data, display_overall_party_data
from company_handler import (
    display_individual_company_data,
    display_overall_company_data,
)
from company_visualization_hadler import display_overall_company_visualization
from data_preprocessing import summarize_data, summarize_party_data


def main():
    # Load and prepare company data from CSV.
    companies = load_and_prepare_data('data/Electoral Bonds - Donors-list-category.csv')

    # Load and prepare party data from CSV.
    parties = load_and_prepare_party_data('data/Electoral Bonds - Party-list.csv')

    # Summarize company data to get sorted lists and grouped data for display.
    sorted_company, year_company_group, parent_company_group, category_group = (
        summarize_data(companies)
    )

    # Summarize party data to get sorted lists and yearly grouped data for display.
    sorted_party, party_year_group = summarize_party_data(parties)

    # Display overview and detailed data for companies using the processed data.
    display_overall_company_data(
        sorted_company, parent_company_group, category_group, company_ov_data
    )
    display_overall_company_visualization(
        sorted_company, parent_company_group, category_group, companies, company_ov_vi
    )
    display_individual_company_data(
        year_company_group, sorted_company, companies, parties, company_i
    )

    # Display overview and detailed data for parties using the processed data.
    display_overall_party_data(sorted_party, party_ov)
    display_individual_party_data(party_year_group, sorted_party, parties, party_i)

    # Display the latest news or relevant information.
    display_news(news_i)


if __name__ == "__main__":
    # Configure the Streamlit page with a wide layout and a custom title and icon.
    st.set_page_config(
        layout="wide",
        page_title="Decoding Indian Electoral Bonds: An In-depth Analysis",
        page_icon="🧊",
    )
    st.info(
        "🔍 Notice Any Data Discrepancies?  Your insights help us improve. If you spot any discrepancies or anomalies in the data presented, please don't hesitate to let us know. You can reach out to us via [https://docs.google.com/forms/d/e/1FAIpQLSf88Fls31Py3B-89Ihb7qeXdS8gxJW6NWWe0ZDL7RzqkvLYQg/viewform?usp=sf_link]. Your feedback is invaluable in ensuring the accuracy and reliability of our data. Thank you for contributing to the quality of our service!",
        icon="ℹ️",
    )
    # Load custom CSS for styling via Streamlit's HTML capabilities.
    st.write(
        '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">',
        unsafe_allow_html=True,
    )

    

    # Set the page title for the analysis.
    st.title("Decoding Indian Electoral Bonds: An In-depth Analysis")

    # Create tabs for organizing the display of company and party data, and news.
    company_ov, company_i, party_ov, party_i, news_i = st.tabs(
        [
            "Company - OverAll",
            "Company - Individual",
            "Party - OverAll",
            "Party - Individual",
            "News",
        ]
    )

    company_ov_data, company_ov_vi = company_ov.tabs(["Data", "Visualization"])

    # Execute the main function to run the app.
    main()
