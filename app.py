import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import urllib.parse
import matplotlib.pyplot as plt
import json


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


def format_amount(amount):
    """
    Format the amount to represent it in Crores (₹ Cr) and append the formatted string representation.

    Parameters:
    - amount: The amount in basic units to be converted and formatted.

    Returns:
    - A formatted string representing the amount in Crores with two decimal places.
    """
    return "{:,.2f}".format(amount / 10**7)


def calculate_percentage(part, whole):
    """
    Calculate the percentage of 'part' with respect to 'whole' and format it as a string.

    Parameters:
    - part: The part value.
    - whole: The whole value against which the percentage is calculated.

    Returns:
    - A string representing the percentage value with two decimal places followed by a percent sign.
    """
    return "{:.2f}%".format(part / whole * 100)


def aggregate_data(group_by_columns, agg_columns, data):
    """
    Aggregates the data based on specified columns and aggregation rules.

    Parameters:
    - group_by_columns: List of columns to group by.
    - agg_columns: Dictionary specifying columns to aggregate and how to aggregate them.
    - data: DataFrame to aggregate.

    Returns:
    - DataFrame with aggregated data.
    """

    grouped_data = data.groupby(group_by_columns).agg(agg_columns)
    column_names = list(agg_columns.keys())
    del column_names[-1]
    column_names.append("Amount")
    column_names.append("Bond_count")
    grouped_data.columns = column_names

    grouped_data["Amount (₹ Cr)"] = grouped_data["Amount"].apply(format_amount)
    grouped_data["percentage"] = grouped_data["Amount"].apply(
        lambda x: calculate_percentage(x, grouped_data["Amount"].sum())
    )

    return grouped_data


def summarize_data(companies):
    """
    Summarizes company data into various aggregated groups.

    Parameters:
    - companies: DataFrame containing company data.

    Returns:
    - Tuple of DataFrames containing aggregated data for company, year-company, parent company, and category groups.
    """

    year_company_group = aggregate_data(
        ["Year", "Company"],
        {
            "Company": "first",
            "Category": "first",
            "Year": "first",
            "Amount": ["sum", "count"],
        },
        companies,
    )
    company_group = aggregate_data(
        ["Company"],
        {"Company": "first", "Category": "first", "Amount": ["sum", "count"]},
        companies,
    )
    parent_company_group = aggregate_data(
        ["Parent Company"],
        {"Amount": ["sum", "count"]},
        companies,
    )
    category_group = aggregate_data(
        ["Category"],
        {"Category": "first", "Amount": ["sum", "count"]},
        companies,
    )

    company_group = company_group.sort_values("Amount", ascending=False)
    parent_company_group = parent_company_group.sort_values("Amount", ascending=False)
    category_group = category_group.sort_values("Amount", ascending=False)

    return company_group, year_company_group, parent_company_group, category_group


def summarize_party_data(parties):
    # Group data by Year and Party, then aggregate to compute the sum and count of Amount for each group.
    # This creates a multi-level DataFrame with each party's total contributions and counts per year.
    party_year_group = parties.groupby(["Year", "party"]).agg(
        {"party": "first", "Year": "first", "Amount": ["sum", "count"]}
    )
    # Flatten the column multi-index and rename for clarity.
    party_year_group.columns = ["party", "Year", "Amount", "Bond_count"]

    # Group data by Party only, to compute the sum and count of Amount for each party across all years.
    party_group = parties.groupby("party").agg(
        {"party": "first", "Amount": ["sum", "count"]}
    )
    # Again, flatten the column multi-index and rename for clarity.
    party_group.columns = ["party", "Amount", "Bond_count"]

    # Convert the total amount to crores for readability, formatting the result.
    party_group["Amount (₹ Cr)"] = (party_group["Amount"] / 10**7).map("{:,.2f}".format)

    # Calculate the percentage share of each party's total contributions from the overall sum.
    # This highlights each party's share of total electoral bonds.
    party_group["percentage"] = (
        party_group["Amount"] / party_group["Amount"].sum() * 100
    ).map("{:.2f}%".format)

    # Return two DataFrames: 
    # 1. party_group sorted by Amount in descending order for overall party rankings.
    # 2. party_year_group with detailed yearly contributions and counts for further analysis.
    return party_group.sort_values("Amount", ascending=False), party_year_group



def create_google_search_url(company, date):
    date_obj = datetime.strptime(date, "%d/%b/%Y")
    three_months_before = date_obj - timedelta(days=60)
    three_months_after = date_obj + timedelta(days=60)
    cd_min = three_months_before.strftime("%m/%d/%Y")
    cd_max = three_months_after.strftime("%m/%d/%Y")
    query = f"{company.lower()}"
    encoded_query = urllib.parse.quote(query)
    url = f"https://www.google.com/search?q={encoded_query}&tbs=cdr:1,cd_min:{cd_min},cd_max:{cd_max}"
    return url


def make_clickable(link, text):
    # Streamlit uses Markdown to render text, so you can use an anchor tag for the link
    return f"[{text}]({link})"

    # Adding a column to the DataFrame with the clickable links


def display_metrics(company_ov, sorted_company):
    """
    Displays key metrics about companies.

    Parameters:
    - company_ov: Streamlit container for displaying data.
    - sorted_company: DataFrame containing sorted company data.
    """
    total_company, total_amount, total_bond_count = company_ov.columns(3)
    total_company.metric("Total Companies", len(sorted_company))
    total_amount.metric("Total Amount (₹ Cr)", sorted_company["Amount"].sum() / 10**7)
    total_bond_count.metric("Total Bonds", sorted_company["Bond_count"].sum())


def display_overview(company_ov, sorted_company):
    """
    Displays a comprehensive overview of electoral bond contributions.

    Parameters:
    - company_ov: Streamlit container for displaying data.
    - sorted_company: DataFrame containing sorted company data.
    """
    company_ov.subheader("Comprehensive Overview of Electoral Bond Contributions")
    company_ov.markdown("---")
    company_ov.dataframe(
        sorted_company.drop(["Company"], axis=1), use_container_width=True
    )


def display_pie_chart(company_ov, sorted_company):
    """
    Displays a pie chart of top 5 companies' contributions and others.

    Parameters:
    - company_ov: Streamlit container for displaying data.
    - sorted_company: DataFrame containing sorted company data.
    """
    top_5_df = sorted_company.head(5)
    others = pd.DataFrame(
        data={"Company": ["Other"], "Amount": [sorted_company["Amount"][5:].sum()]}
    )
    combined_df = pd.concat([top_5_df, others])

    fig, ax = plt.subplots()
    ax.pie(
        combined_df["Amount"],
        labels=combined_df["Company"],
        autopct="%1.1f%%",
        startangle=140,
    )
    ax.axis("equal")  # Equal aspect ratio ensures that pie is drawn as a circle.
    company_ov.pyplot(fig)


def display_category_data(company_ov, category_group, sorted_company):
    """
    Displays data and allows interaction based on categories.

    Parameters:
    - company_ov: Streamlit container for displaying data.
    - category_group: DataFrame of aggregated category data.
    - sorted_company: DataFrame containing sorted company data.
    """
    col1, col2 = company_ov.columns([3, 3])
    with col1:
        col1.subheader("Top Donor Categories by Electoral Bond Contributions")
        col1.dataframe(
            category_group[["Category", "Bond_count", "Amount (₹ Cr)", "percentage"]],
            use_container_width=True,
        )

    with col2:
        col2.subheader("Explore Companies by Category")
        selected_category = col2.selectbox(
            "Select a Category", category_group["Category"]
        )
        category_companies = sorted_company[
            sorted_company["Category"] == selected_category
        ].reset_index(drop=True)
        category_companies["percentage"] = (
            category_companies["Amount"] / category_companies["Amount"].sum() * 100
        ).map("{:.2f}%".format)

        col2.dataframe(
            category_companies[["Company", "Bond_count", "Amount (₹ Cr)", "percentage"]]
        )


def display_major_contributors(company_ov, parent_company_group):
    """
    Displays a DataFrame of major contributing entities to electoral bonds.

    Parameters:
    - company_ov: Streamlit container for displaying data.
    - parent_company_group: DataFrame of aggregated parent company data.
    """
    company_ov.subheader("Major Contributing Entities to Electoral Bonds")
    company_ov.dataframe(parent_company_group, use_container_width=True)


def display_top_and_bottom_donors(company_ov, sorted_company):
    """
    Displays bar charts for top and bottom donor companies.

    Parameters:
    - company_ov: Streamlit container for displaying data.
    - sorted_company: DataFrame containing sorted company data.
    """
    top_10_df = sorted_company.head(10)
    bottom_10_df = sorted_company.tail(10)

    company_ov.subheader("Leading Donor Companies by Electoral Bond Contributions")
    company_ov.bar_chart(top_10_df.set_index("Company")["Amount"])

    company_ov.subheader("Smallest Donor Companies by Electoral Bond Contributions")
    company_ov.bar_chart(bottom_10_df.set_index("Company")["Amount"])


def display_overall_company_data(
    sorted_company, parent_company_group, category_group, company_ov
):
    """
    Modular function to display overall company data.

    Parameters:
    - sorted_company: DataFrame of sorted company data.
    - parent_company_group: DataFrame of aggregated parent company data.
    - category_group: DataFrame of aggregated category data.
    - company_ov: Streamlit container or page to display the data on.
    """
    display_metrics(company_ov, sorted_company)
    display_overview(company_ov, sorted_company)
    # display_pie_chart(company_ov, sorted_company) # Uncomment if pie chart display is desired
    display_category_data(company_ov, category_group, sorted_company)
    display_major_contributors(company_ov, parent_company_group)
    display_top_and_bottom_donors(company_ov, sorted_company)


def display_overall_party_data(sorted_party):
    col1, col2 = party_ov.columns([3, 3])
    with col1:
        col1.subheader("Total Electoral Bond Redemption Data")
        col1.markdown("---")
        col1.dataframe(sorted_party.drop(["party"], axis=1))
    top_10_df = sorted_party.head(10)
    top_5_df = sorted_party.head(6)
    others = pd.DataFrame(
        data={"party": ["Other"], "Amount": [sorted_party["Amount"][6:].sum()]}
    )
    combined_df = pd.concat([top_5_df, others])
    # Plotting
    fig, ax = plt.subplots()
    wedges, texts, autotexts = ax.pie(
        combined_df["Amount"],
        labels=combined_df["party"],
        autopct="%1.1f%%",
        startangle=140,
    )
    ax.legend(
        wedges,
        combined_df["party"],
        title="Parties",
        loc="lower center",
        bbox_to_anchor=(1, 0, 0.5, 1),
    )
    # centre_circle = plt.Circle((0,0),0.70,fc='white')
    # fig.gca().add_artist(centre_circle)
    ax.axis("equal")  # Equal aspect ratio ensures that pie is drawn as a circle.
    with col2:
        col2.subheader("Distribution of Top Electoral Bond Redemption party")
        col2.markdown("---")
        col2.pyplot(fig)

    with col1:
        col1.subheader("Top 10 Highest Electoral Bond Redemptions")
        col1.markdown("---")
        col1.bar_chart(top_10_df.set_index("party")["Amount"])
    bottom_10_df = sorted_party.tail(10)

    with col2:
        col2.subheader("Top 10 Lowest Electoral Bond Redemptions")
        col2.markdown("---")
        col2.bar_chart(bottom_10_df.set_index("party")["Amount"])


def select_company(company_i, sorted_company):
    """
    Allows user to select a company from a dropdown and returns the selected company name.
    
    Parameters:
    - company_i: Streamlit container for displaying the selection box.
    - sorted_company: DataFrame containing sorted company data.
    
    Returns:
    - The name of the selected company.
    """
    return company_i.selectbox("Select a Company", sorted_company["Company"])

def display_company_transactions(company_i, companies, selected_company):
    """
    Displays transactions of the selected company with a link to related news.
    
    Parameters:
    - company_i: Streamlit container for displaying data.
    - companies: DataFrame containing company transaction data.
    - selected_company: The name of the selected company.
    """
    company_transaction_details = companies[
        companies["Company"] == selected_company
    ].reset_index(drop=True)
    company_i.subheader("Detailed Donor Contributions by Date")
    company_i.markdown("---")
    query = f"{selected_company.lower()} when:1y"
    encoded_query = urllib.parse.quote(query)
    url = f"https://news.google.com/search?q={encoded_query}"
    link_text = "News"
    company_i.markdown(f'<a href="{url}" target="_blank">{link_text}</a>', unsafe_allow_html=True)
    company_i.dataframe(company_transaction_details[["Date", "Company", "Amount"]])

def display_aggregate_transactions(company_i, sorted_company, selected_company):
    """
    Displays aggregate transaction overview for the selected company.
    
    Parameters:
    - company_i: Streamlit container for displaying data.
    - sorted_company: DataFrame containing sorted company data.
    - selected_company: The name of the selected company.
    """
    overall_transaction_details = sorted_company[
        sorted_company["Company"] == selected_company
    ].reset_index(drop=True)
    company_i.subheader("Aggregate Donor Transaction Overview")
    company_i.markdown("---")
    company_i.dataframe(overall_transaction_details)

def display_annual_contributions(company_i, year_company_group, selected_company):
    """
    Displays annual contributions of the selected company.
    
    Parameters:
    - company_i: Streamlit container for displaying data.
    - year_company_group: DataFrame containing annual company group data.
    - selected_company: The name of the selected company.
    """
    selected_company_year_spendings = year_company_group[
        year_company_group["Company"] == selected_company
    ].reset_index(drop=True)
    selected_company_year_spendings["Year"] = selected_company_year_spendings["Year"].astype(str)
    selected_company_year_spendings["Amount (₹ Cr)"] = (
        selected_company_year_spendings["Amount"] / 10**7
    )
    
    col1, col2 = company_i.columns([3, 3])
    
    with col1:
        col1.subheader("Annual Donor Contributions via Electoral Bonds")
        col1.markdown("---")
        col1.dataframe(selected_company_year_spendings)

    with col2:
        col2.subheader("Yearly Trends in Electoral Bond Contributions")
        col2.markdown("---")
        col2.line_chart(selected_company_year_spendings.set_index("Year")["Amount"])

def display_individual_company_data(year_company_group, sorted_company, companies, company_i):
    """
    Modular function to display data for an individual company, including transaction details,
    aggregate transactions, and annual contributions.
    
    Parameters:
    - year_company_group: DataFrame containing annual company group data.
    - sorted_company: DataFrame containing sorted company data.
    - companies: DataFrame containing company transaction data.
    - company_i: Streamlit container or page to display the data on.
    """
    selected_company = select_company(company_i, sorted_company)
    display_aggregate_transactions(company_i, sorted_company, selected_company)
    display_annual_contributions(company_i, year_company_group, selected_company)
    display_company_transactions(company_i, companies, selected_company)



def select_party(party_i, sorted_party):
    """
    Allows user to select a party from a dropdown.
    
    Parameters:
    - party_i: Streamlit container for displaying the selection box.
    - sorted_party: DataFrame containing sorted party data.
    
    Returns:
    - The name of the selected party.
    """
    return party_i.selectbox("Select a Party", sorted_party["party"].sort_values())

def display_party_transactions(party_i, parties, selected_party):
    """
    Displays transactions of the selected party.
    
    Parameters:
    - party_i: Streamlit container for displaying data.
    - parties: DataFrame containing party transaction data.
    - selected_party: The name of the selected party.
    """
    party_transaction_details = parties[parties["party"] == selected_party].reset_index(drop=True)
    party_i.subheader("Date-specific Bond Redemption Details")
    party_i.markdown("---")
    party_i.dataframe(party_transaction_details[["Date", "party", "Amount"]])

def display_overall_transactions(party_i, sorted_party, selected_party):
    """
    Displays overall transaction overview for the selected party.
    
    Parameters:
    - party_i: Streamlit container for displaying data.
    - sorted_party: DataFrame containing sorted party data.
    - selected_party: The name of the selected party.
    """
    overall_transaction_details = sorted_party[
        sorted_party["party"] == selected_party
    ].reset_index(drop=True)
    overall_transaction_details["Bond Count"] = overall_transaction_details.shape[0]
    party_i.subheader("Comprehensive Transaction Overview")
    party_i.markdown("---")
    party_i.dataframe(overall_transaction_details)

def display_annual_party_contributions(party_i, party_year_group, selected_party):
    """
    Displays annual contributions of the selected party.
    
    Parameters:
    - party_i: Streamlit container for displaying data.
    - party_year_group: DataFrame containing annual party group data.
    - selected_party: The name of the selected party.
    """
    print(party_year_group.columns)
    selected_party_year_spendings = party_year_group[
        party_year_group["party"] == selected_party
    ].reset_index(drop=True)
    selected_party_year_spendings["Year"] = selected_party_year_spendings["Year"].astype(str)
    selected_party_year_spendings["Amount (₹ Cr)"] = (
        selected_party_year_spendings["Amount"] / 10**7
    )
    
    col1, col2 = party_i.columns([3, 3])
    with col1:
        col1.subheader("Annual Electoral Bond Redemption Summary")
        col1.dataframe(selected_party_year_spendings)

    with col2:
        col2.subheader("Yearly Electoral Bond Redemptions Trend")
        col2.line_chart(selected_party_year_spendings.set_index("Year")["Amount"])

def display_individual_party_data(party_year_group, sorted_party, parties, party_i):
    """
    Modular function to display data for an individual party, including transaction details,
    aggregate transactions, and annual contributions.
    
    Parameters:
    - party_year_group: DataFrame containing annual party group data.
    - sorted_party: DataFrame containing sorted party data.
    - parties: DataFrame containing party transaction data.
    - party_i: Streamlit container or page to display the data on.
    """
    selected_party = select_party(party_i, sorted_party)
    display_overall_transactions(party_i, sorted_party, selected_party)
    display_annual_party_contributions(party_i, party_year_group, selected_party)
    display_party_transactions(party_i, parties, selected_party)


def generate_news_links(articles):
    """
    Generates HTML markup for news article links.
    
    Parameters:
    - articles: A dictionary where keys are article titles and values are article URLs.
    
    Returns:
    - A list of HTML strings for each news link.
    """
    return [f'<a href="{url}" target="_blank">{title}</a>' for title, url in articles.items()]

def display_news_links(news_i, news_links):
    """
    Displays news links on the provided Streamlit container.
    
    Parameters:
    - news_i: The Streamlit container or page to display the news links on.
    - news_links: A list of HTML strings containing news links.
    """
    for link in news_links:
        news_i.markdown(link, unsafe_allow_html=True)

def load_articles_from_json(json_file_path):
    """
    Loads news articles from a JSON file.
    
    Parameters:
    - json_file_path: Path to the JSON file containing news articles.
    
    Returns:
    - A dictionary where keys are article titles and values are article URLs.
    """
    with open(json_file_path, 'r') as file:
        data = json.load(file)
    articles = {article['title']: article['url'] for article in data['articles']}
    return articles

def display_news(news_i):
    """
    Displays a list of news articles on a Streamlit container or page.
    
    Parameters:
    - news_i: The Streamlit container or page to display the news on.
    """
    articles = load_articles_from_json('articles.json')
    news_links = generate_news_links(articles)
    display_news_links(news_i, news_links)


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
    display_overall_party_data(sorted_party)
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