import urllib.parse
import matplotlib.pyplot as plt
import pandas as pd

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