import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import urllib.parse
import matplotlib.pyplot as plt

def load_and_prepare_data(csv_file):
    companies = pd.read_csv(csv_file)
    companies = companies.rename(columns={'Date of Purchase': 'Date'})
    replacements = {
        r'FUTURE GAMING AND HOTEL SERVICES.*': 'FUTURE GAMING AND HOTEL SERVICES PRIVATE LTD',
        r'AASHMAN ENERGY.*': 'AASHMAN ENERGY PRIVATE LIMITED',
        r'APCO INFRATECH.*': 'APCO INFRATECH PRIVATE LIMITED',
        r'MEGHA ENGINEERING.*': 'MEGHA ENGINEERING AND INFRASTRUCTURES LIMITED'
    }
    for pattern, replacement in replacements.items():
        companies['Company'] = companies['Company'].str.replace(pattern, replacement, regex=True)

    companies['Amount'] = companies['Amount'].str.replace(",", "").astype(float).astype('int64')
    companies['Date_format'] = pd.to_datetime(companies['Date'], format='%d/%b/%Y')
    companies['Year'] = companies['Date_format'].dt.year
    companies['Category'] = companies['Category'].str.lower().str.title()
    companies['Parent Company'] = companies['Parent Company'].str.lower().str.title()
    return companies

def load_and_prepare_party_data(csv_file):
    parties = pd.read_csv(csv_file)
    # replacements = {
    #     r'FUTURE GAMING AND HOTEL SERVICES.*': 'FUTURE GAMING AND HOTEL SERVICES PRIVATE LTD',
    #     r'AASHMAN ENERGY.*': 'AASHMAN ENERGY PRIVATE LIMITED',
    #     r'APCO INFRATECH.*': 'APCO INFRATECH PRIVATE LIMITED'
    # }
    # for pattern, replacement in replacements.items():
    #     parties['Company'] = parties['Company'].str.replace(pattern, replacement, regex=True)

    parties['Amount'] = parties['Amount'].str.replace(",", "").astype(float).astype('int64')
    parties['Date_format'] = pd.to_datetime(parties['Date'], format='%d/%b/%Y')
    parties['Year'] = parties['Date_format'].dt.year
    return parties

def summarize_data(companies):
    year_company_group = companies.groupby(['Year', 'Company']).agg({'Company':'first','Year':'first', 'Amount':['sum', 'count']})
    year_company_group.columns = ['Company', 'Year', 'Amount', 'Bond_count']
    company_group = companies.groupby("Company").agg({'Company':'first', 'Amount':['sum', 'count']})
    company_group.columns = ['Company', 'Amount', 'Bond_count']
    company_group['Amount (₹ Cr)'] = (company_group['Amount'] / 10**7).map("{:,.2f}".format)
    company_group['percentage'] = (company_group['Amount'] / company_group['Amount'].sum() * 100).map('{:.2f}%'.format)
    parent_company_group = companies.groupby(['Parent Company']).agg({ 'Amount':['sum', 'count']})
    parent_company_group.columns = ['Amount', 'Bond_count']
    category_group = companies.groupby(['Category']).agg({'Amount':['sum', 'count']})
    category_group.columns = ['Amount', 'Bond_count']
    category_group['Amount (₹ Cr)'] = (category_group['Amount'] / 10**7).map("{:,.2f}".format)
    parent_company_group['Amount (₹ Cr)'] = (parent_company_group['Amount'] / 10**7).map("{:,.2f}".format)
    return company_group.sort_values("Amount", ascending=False), year_company_group, parent_company_group.sort_values("Amount", ascending=False), category_group.sort_values("Amount", ascending=False)

def summarize_party_data(parties):
    party_year_group = parties.groupby(['Year', 'party']).agg({'party':'first','Year':'first', 'Amount':['sum', 'count']})
    party_year_group.columns = ['party', 'Year', 'Amount', 'Bond_count']
    party_group = parties.groupby("party").agg({'party':'first', 'Amount':['sum', 'count']})
    party_group.columns = ['party', 'Amount', 'Bond_count']
    party_group['Amount (₹ Cr)'] = (party_group['Amount'] / 10**7).map("{:,.2f}".format)
    party_group['percentage'] = (party_group['Amount'] / party_group['Amount'].sum() * 100).map('{:.2f}%'.format)
    return party_group.sort_values("Amount", ascending=False), party_year_group

def create_google_search_url(company, date):
    date_obj = datetime.strptime(date, '%d/%b/%Y')
    three_months_before = date_obj - timedelta(days=60)
    three_months_after = date_obj + timedelta(days=60)
    cd_min = three_months_before.strftime('%m/%d/%Y')
    cd_max = three_months_after.strftime('%m/%d/%Y')
    query = f"{company.lower()}"
    encoded_query = urllib.parse.quote(query)
    url = f"https://www.google.com/search?q={encoded_query}&tbs=cdr:1,cd_min:{cd_min},cd_max:{cd_max}"
    return url

def display_overall_company_data(sorted_company, parent_company_group, category_group):
    total_company, Total_amount, Total_Bond_count = company_ov.columns(3)
    total_company.metric("Total Companies", len(sorted_company))
    Total_amount.metric("Total Amount (₹ Cr)", sorted_company['Amount'].sum()/ 10**7)
    Total_Bond_count.metric("Total Bonds", sorted_company['Bond_count'].sum())

    company_ov.markdown("---")
    # with col1:
    company_ov.subheader("Comprehensive Overview of Electoral Bond Contributions")
    company_ov.markdown("---")
    company_ov.dataframe(sorted_company.drop(['Company'], axis=1), use_container_width=True)
    top_10_df = sorted_company.head(10)
    top_5_df = sorted_company.head(5)
    others = pd.DataFrame(data={
                'Company': ['Other'],
                'Amount': [sorted_company['Amount'][5:].sum()]
            })
    combined_df = pd.concat([top_5_df, others])
    bottom_10_df = sorted_company.tail(10)
     # Plotting
    fig, ax = plt.subplots()
    ax.pie(combined_df['Amount'], labels=combined_df['Company'], autopct='%1.1f%%', startangle=140)
    # centre_circle = plt.Circle((0,0),0.70,fc='white')
    # fig.gca().add_artist(centre_circle)
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.  
    # company_ov.subheader("Distribution of Top Electoral Bond Contributions by Company")
    # company_ov.markdown("---")
    # company_ov.pyplot(fig)
    
    company_ov.subheader("Top Donor Categories by Electoral Bond Contributions")
    company_ov.markdown("---")
    company_ov.dataframe(category_group, use_container_width=True)


    company_ov.subheader("Major Contributing Entities to Electoral Bonds")
    company_ov.markdown("---")
    company_ov.dataframe(parent_company_group, use_container_width=True)


    company_ov.subheader("Leading Donor Companies by Electoral Bond Contributions")
    company_ov.markdown("---")

    company_ov.bar_chart(top_10_df.set_index('Company')['Amount'])


    company_ov.subheader("Smallest Donor Companies by Electoral Bond Contributions")
    company_ov.markdown("---")
    company_ov.bar_chart(bottom_10_df.set_index('Company')['Amount'])


def display_overall_party_data(sorted_party):
    col1, col2 = party_ov.columns([3, 3])
    with col1:
        col1.subheader("Total Electoral Bond Redemption Data")
        col1.markdown("---")
        col1.dataframe(sorted_party.drop(['party'], axis=1))
    top_10_df = sorted_party.head(10)
    top_5_df = sorted_party.head(6)
    others = pd.DataFrame(data={
                'party': ['Other'],
                'Amount': [sorted_party['Amount'][6:].sum()]
            })
    combined_df = pd.concat([top_5_df, others])
     # Plotting
    fig, ax = plt.subplots()
    wedges, texts, autotexts = ax.pie(combined_df['Amount'], labels=combined_df['party'], autopct='%1.1f%%', startangle=140)
    ax.legend(wedges, combined_df['party'], title="Parties", loc="lower center", bbox_to_anchor=(1, 0, 0.5, 1))
    # centre_circle = plt.Circle((0,0),0.70,fc='white')
    # fig.gca().add_artist(centre_circle)
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    with col2:
        col2.subheader("Distribution of Top Electoral Bond Redemption party")
        col2.markdown("---")
        col2.pyplot(fig)

    with col1:
        col1.subheader("Top 10 Highest Electoral Bond Redemptions")
        col1.markdown("---")
        col1.bar_chart(top_10_df.set_index('party')['Amount'])
    bottom_10_df = sorted_party.tail(10)
    
    with col2:
        col2.subheader("Top 10 Lowest Electoral Bond Redemptions")
        col2.markdown("---")
        col2.bar_chart(bottom_10_df.set_index('party')['Amount'])

def display_individual_company_data(year_company_group, sorted_company , companies):
    
    selected_company = company_i.selectbox(
        "Select an Company",
        sorted_company['Company']
    )
    company_transaction_details = companies[companies['Company'] == selected_company].reset_index(drop=True)
    company_transaction_details['News'] = company_transaction_details.apply(lambda x: f"<a href='{create_google_search_url(x['Company'], x['Date'])}' target='_blank'>6 month news </a>", axis=1)
    overall_transaction_details = sorted_company[sorted_company['Company'] == selected_company].reset_index(drop=True)
    selected_company_year_spendings = year_company_group[year_company_group['Company'] == selected_company].reset_index(drop=True)
    selected_company_year_spendings['Year'] = selected_company_year_spendings['Year'].astype(str)
    selected_company_year_spendings['Amount (₹ Cr)'] = selected_company_year_spendings['Amount'] / 10**7
    
    company_i.subheader("Aggregate Donor Transaction Overview")
    company_i.markdown("---")
    company_i.dataframe(overall_transaction_details)
    col1, col2 = company_i.columns([3, 3])
    with col1:
        col1.subheader("Annual Donor Contributions via Electoral Bonds")
        col1.markdown("---")
        col1.dataframe(selected_company_year_spendings)
    
    with col2:
        col2.subheader("Yearly Trends in Electoral Bond Contributions")
        col2.markdown("---")
        col2.line_chart(selected_company_year_spendings.set_index('Year')['Amount'])
    
    company_i.subheader("Detailed Donor Contributions by Date")
    company_i.markdown("---")
    query = f"{selected_company.lower()} when:1y"
    encoded_query = urllib.parse.quote(query)
    url = f"https://news.google.com/search?q={encoded_query}"
    link_text = "News"
    company_i.markdown(f'<a href="{url}" target="_blank">{link_text}</a>', unsafe_allow_html=True)
    company_i.dataframe(company_transaction_details[['Date','Company','Amount']]) #.to_html(escape=False, index=False), unsafe_allow_html=True)

def display_individual_party_data(party_year_group, sorted_party, parties):
    selected_party = party_i.selectbox(
        "Select an Party",
        sorted_party['party'].sort_values()
    )
    party_transaction_details = parties[parties['party'] == selected_party].reset_index(drop=True)
    # company_transaction_details['News'] = company_transaction_details.apply(lambda x: f"<a href='{create_google_search_url(x['party'], x['Date'])}' target='_blank'>6 month news </a>", axis=1)
    overall_transaction_details = sorted_party[sorted_party['party'] == selected_party].reset_index(drop=True)
    overall_transaction_details['Bond Count'] = len(party_transaction_details.index)
    selected_party_year_spendings = party_year_group[party_year_group['party'] == selected_party].reset_index(drop=True)
    selected_party_year_spendings['Year'] = selected_party_year_spendings['Year'].astype(str)
    selected_party_year_spendings['Amount (₹ Cr)'] = selected_party_year_spendings['Amount'] / 10**7

    
    party_i.subheader("Comprehensive Transaction Overview")
    party_i.markdown("---")
    party_i.dataframe(overall_transaction_details)
    col1, col2 = party_i.columns([3, 3])
    with col1:
        col1.subheader("Annual Electoral Bond Redemption Summary")
        col1.markdown("---")
        col1.dataframe(selected_party_year_spendings)
    with col2:
        col2.subheader("Yearly Electoral Bond Redemptions Trend")
        col2.markdown("---")
        col2.line_chart(selected_party_year_spendings.set_index('Year')['Amount'])
    party_i.subheader("Date-specific Bond Redemption Details")
    party_i.markdown("---")
    party_i.dataframe(party_transaction_details[['Date','party','Amount']])
    # st.markdown(company_transaction_details[['Date','party','Amount']].to_html(escape=False, index=False), unsafe_allow_html=True)

    st.divider()

# Assuming other display functions follow a similar pattern to display_overall_company_data

def main():
    companies = load_and_prepare_data('Electoral Bonds - Donors-list-category.csv')
    parties = load_and_prepare_party_data('Electoral Bonds - Party-list.csv')
    sorted_company, year_company_group, parent_company_group, category_group = summarize_data(companies)
    sorted_party, party_year_group = summarize_party_data(parties)
    
    display_overall_company_data(sorted_company, parent_company_group, category_group)

    display_individual_company_data(year_company_group, sorted_company, companies)

    display_overall_party_data(sorted_party)

    display_individual_party_data(party_year_group, sorted_party, parties)

if __name__ == "__main__":
    st.set_page_config(layout="wide", page_title="Decoding Indian Electoral Bonds: An In-depth Analysis", page_icon="🧊",)
    st.write('<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">', unsafe_allow_html=True)
    st.title("Decoding Indian Electoral Bonds: An In-depth Analysis")
    company_ov, company_i, party_ov, party_i = st.tabs(['Company - OverAll', "Company - Individual", "Party - OverAll", "Party - Individual"])
    main()
