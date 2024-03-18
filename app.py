import streamlit as st
from data_loader import load_and_prepare_data, load_and_prepare_party_data
from news_handler import display_news
from party_handler import display_individual_party_data, display_overall_party_data
from company_handler import display_individual_company_data, display_overall_company_data
from data_preprocessing import summarize_data, summarize_party_data

def main():
    # Load and prepare company data from CSV.
    companies = load_and_prepare_data("Electoral Bonds - Donors-list-category.csv")
    
    # Load and prepare party data from CSV.
    parties = load_and_prepare_party_data("Electoral Bonds - Party-list.csv")
    
    # Summarize company data to get sorted lists and grouped data for display.
    sorted_company, year_company_group, parent_company_group, category_group = (
        summarize_data(companies)
    )
    
    # Summarize party data to get sorted lists and yearly grouped data for display.
    sorted_party, party_year_group = summarize_party_data(parties)
    
    # Display overview and detailed data for companies using the processed data.
    display_overall_company_data(
        sorted_company, parent_company_group, category_group, company_ov
    )
    display_individual_company_data(year_company_group, sorted_company, companies, company_i)
    
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
    
    # Execute the main function to run the app.
    main()