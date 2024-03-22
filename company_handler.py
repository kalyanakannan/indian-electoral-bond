import urllib.parse
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from streamlit_echarts import st_echarts
from utils import calculate_percentage, format_amount

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

def add_open_corporate_url(url):
    url_prefix  = "https://opencorporates.com/companies/in/"
    if url:
        url = url_prefix + url
    return url

def display_overview(company_ov, sorted_company):
    """
    Displays a comprehensive overview of electoral bond contributions.

    Parameters:
    - company_ov: Streamlit container for displaying data.
    - sorted_company: DataFrame containing sorted company data.
    """
    company_ov.subheader("Comprehensive Overview of Electoral Bond Contributions")
    
    sorted_company['company_details'] = sorted_company['company_id'].apply(add_open_corporate_url)
    # sorted_company = sorted_company.drop([" "], axis=1)
    sorted_company = sorted_company.reset_index(drop=True)
    company_ov.markdown("---")
    company_ov.dataframe(
        sorted_company[['Company', 'Category', 'Bond_count', 'Amount', 'Amount (₹ Cr)', 'percentage', 'company_details']] , use_container_width=True, column_config={
        "company_details": st.column_config.LinkColumn("company_details"),
    }
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
    category_group = category_group.reset_index(drop=True)
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
        if selected_category == 'Individuals':
            col2.dataframe(
                category_companies[["Company", "Parent Company", "Bond_count", "Amount (₹ Cr)", "percentage"]]
            )
        else:
            col2.dataframe(
                category_companies[["Company", "Bond_count", "Amount (₹ Cr)", "percentage"]]
            )


def display_parent_company_data(company_ov, parent_company_group, sorted_company):
    """
    Displays data and allows interaction based on categories.

    Parameters:
    - company_ov: Streamlit container for displaying data.
    - category_group: DataFrame of aggregated category data.
    - sorted_company: DataFrame containing sorted company data.
    """
    col1, col2 = company_ov.columns([3, 3])
    with col1:
        display_major_contributors(col1, parent_company_group)

    with col2:
        col2.subheader("Explore Companies by Parent company")
        selected_parent_company = col2.selectbox(
            "Select a Parent Company", parent_company_group["Parent Company"]
        )
        category_companies = sorted_company[
            sorted_company["Parent Company"] == selected_parent_company
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
    parent_company_group = parent_company_group.reset_index(drop=True)
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
    display_parent_company_data(company_ov, parent_company_group, sorted_company)
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

def display_company_transactions(company_i, merged_df, selected_company):
    """
    Displays transactions of the selected company with a link to related news.
    
    Parameters:
    - company_i: Streamlit container for displaying data.
    - companies: DataFrame containing company transaction data.
    - selected_company: The name of the selected company.
    """
    company_transaction_details = merged_df[
        merged_df["Company"] == selected_company
    ].reset_index(drop=True)
    company_i.subheader("Detailed Donor Contributions by Date")
    company_i.markdown("---")
    query = f"{selected_company.lower()} when:1y"
    encoded_query = urllib.parse.quote(query)
    url = f"https://news.google.com/search?q={encoded_query}"
    link_text = "News"
    company_i.markdown(f'<a href="{url}" target="_blank">{link_text}</a>', unsafe_allow_html=True)
    company_i.dataframe(company_transaction_details[["Date_x", "Reference No  (URN)", "Journal Date", "party", "Amount_x", "Prefix","Bond Number"]], column_config={
        "Date_x": "Date",
        "Amount_x": "Amount",
        "party": "party Redeemed"
    }, use_container_width=True)

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

def display_parties_redeemed_bonds(company_i,selected_company, merged_df, company_left):
    companies_transactions = merged_df[
        merged_df["Company"] == selected_company
    ].reset_index(drop=True)
    group_by_parties = companies_transactions.groupby('party').agg({"party": "first","Amount_y": ["sum", "count"]})
    group_by_parties.columns = ['party', 'Amount', 'bond_count']
    group_by_parties["Amount (₹ Cr)"] = group_by_parties["Amount"].apply(format_amount)
    group_by_parties["percentage"] = group_by_parties["Amount"].apply(
        lambda x: calculate_percentage(x, group_by_parties["Amount"].sum())
    )

    company_left.subheader("Parties That Have Redeemed Bonds")
    company_left.markdown("---")
    print(companies_transactions.columns)
    group_by_parties = group_by_parties.reset_index(drop=True)
    group_by_parties = group_by_parties.sort_values("Amount", ascending=False)
    company_left.dataframe(group_by_parties[['party', 'Amount', 'bond_count', 'Amount (₹ Cr)', 'percentage']])

    # company_i.subheader("Parties That Have Redeemed Bonds")
    # company_i.markdown("---")
    # print(companies_transactions.columns)
    # company_i.dataframe(companies_transactions[["Date_y", "party", "Amount_y", "Prefix","Bond Number"]], column_config={
    #     "Date_y": "Date",
    #     "Amount_y": "Amount"
    # })

def top_contributors(company_i, merged_df, selected_company, company_right):
    party_n = company_right.selectbox(
            "Select Number of parties", [5,10,15,20],
        )
    companies_transactions = merged_df[
        merged_df["Company"] == selected_company
    ].reset_index(drop=True)
    group_by_parties = companies_transactions.groupby('party').agg({"party": "first","Amount_y": ["sum", "count"]})
    group_by_parties.columns = ['party', 'Amount', 'bond_count']
    group_by_parties["Amount (₹ Cr)"] = group_by_parties["Amount"].apply(format_amount)
    group_by_parties["percentage"] = group_by_parties["Amount"].apply(
        lambda x: calculate_percentage(x, group_by_parties["Amount"].sum())
    )
    group_by_parties = group_by_parties.sort_values("Amount", ascending=False)

    top_df = group_by_parties.head(party_n)
    others = pd.DataFrame(
        data={"party": ["Other"], "Amount": [group_by_parties["Amount"][party_n:].sum()]}
    )
    others["Amount (₹ Cr)"] = (others["Amount"] / 10**7).map("{:,.2f}".format)
    combined_df = pd.concat([top_df, others])
    combined_df["Amount (₹ Cr)"] = (
        combined_df["Amount (₹ Cr)"].str.replace(",", "").astype(float)
    )
    data = (
        combined_df[["party", "Amount (₹ Cr)"]]
        .rename(columns={"party": "name", "Amount (₹ Cr)": "value"})
        .to_dict("records")
    )
    options = {
       
        "tooltip": {"trigger": "item"},
        "legend": {"orient": "horizontal ", "bottom": "bottom"},
        "dataset": [
            {
                "source": data,
            }
        ],
        "series": [
            {
                "type": "pie",
                "radius": "50%",
            },
            {
                "type": "pie",
                "radius": "50%",
                "label": {
                    "position": "inside",
                    "formatter": "{d}%",
                    "color": "black",
                    "fontSize": 18,
                },
                "emphasis": {
                    "label": {"show": "true"},
                    "itemStyle": {
                        "shadowBlur": 10,
                        "shadowOffsetX": 0,
                        "shadowColor": "rgba(0, 0, 0, 0.5)",
                    },
                },
            },
        ],
    }
    company_right.header(f"Electoral Contributors' for this party")
    with company_right:
        st_echarts(
            options=options,
            height="600px",
        )



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

def display_individual_company_data(year_company_group, sorted_company, companies, merged_df, company_i):
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
    company_right, company_left = company_i.columns([3,3])
    display_parties_redeemed_bonds(company_i, selected_company, merged_df, company_right)
    top_contributors(company_i, merged_df, selected_company, company_left)
    display_annual_contributions(company_i, year_company_group, selected_company)
    display_company_transactions(company_i, merged_df, selected_company)