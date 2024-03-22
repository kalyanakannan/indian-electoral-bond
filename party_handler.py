import matplotlib.pyplot as plt
import pandas as pd
from utils import (
    calculate_percentage,
    format_amount,
    aggregate_transactions,
    format_and_sort_group,
)
from streamlit_echarts import st_echarts


def display_party_transactions(party_i, merged_df, selected_party):
    """
    Displays transactions of the selected party.

    Parameters:
    - party_i: Streamlit container for displaying data.
    - parties: DataFrame containing party transaction data.
    - selected_party: The name of the selected party.
    """
    party_transaction_details = merged_df[
        merged_df["party"] == selected_party
    ].reset_index(drop=True)
    party_i.subheader("Date-specific Bond Redemption Details")
    party_i.markdown("---")
    party_i.dataframe(
        party_transaction_details[
            [
                "Date_y",
                "Reference No  (URN)",
                "Journal Date",
                "Company",
                "Amount_y",
                "Prefix",
                "Bond Number",
            ]
        ],
        column_config={"Date_y": "Date", "Amount_y": "Amount"},
        use_container_width=True,
    )


def display_overall_party_data(sorted_party, party_ov):
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


def display_donated_category(selected_party, merged_df, party_left):
    transactions_grouped_by_category = aggregate_transactions(
        merged_df[merged_df["party"] == selected_party], 'Category', 
        {"Category": "first", "Amount_y": ["sum", "count"]},
    )
    formatted_group = format_and_sort_group(
        transactions_grouped_by_category, format_amount, calculate_percentage
    )

    party_left.subheader("Bonds Details by Category")
    party_left.markdown("---")
    party_left.dataframe(
        formatted_group[
            ["Category", "Amount", "bond_count", "Amount (₹ Cr)", "percentage"]
        ],use_container_width=True
    )


def display_donated_companies(selected_party, merged_df, party_left):

    transactions_grouped_by_category = aggregate_transactions(
        merged_df[merged_df["party"] == selected_party], "Company",
        {"Company": "first", "Parent Company": "first","Category":"first", "Amount_y": ["sum", "count"]},
    )
    formatted_group = format_and_sort_group(
        transactions_grouped_by_category, format_amount, calculate_percentage
    )

    party_left.subheader("List of Company Contributions to This Party")
    party_left.markdown("---")
    party_left.dataframe(
        formatted_group[
            [
                "Company",
                "Parent Company", "Category", "Amount",
                "bond_count",
                "Amount (₹ Cr)",
                "percentage",
            ]
        ], use_container_width=True
    )


def top_contributors_catgory(merged_df, selected_party, party_left):

    party_transactions = merged_df[merged_df["party"] == selected_party].reset_index(
        drop=True
    )
    group_by_categories = party_transactions.groupby("Category").agg(
        {"Category": "first", "Amount_y": ["sum", "count"]}
    )
    group_by_categories.columns = ["Category", "Amount", "bond_count"]
    group_by_categories["Amount (₹ Cr)"] = group_by_categories["Amount"].apply(
        format_amount
    )
    group_by_categories["percentage"] = group_by_categories["Amount"].apply(
        lambda x: calculate_percentage(x, group_by_categories["Amount"].sum())
    )
    group_by_categories = group_by_categories.sort_values("Amount", ascending=False)
    try:
        group_by_categories["Amount (₹ Cr)"] = (
            group_by_categories["Amount (₹ Cr)"].str.replace(",", "").astype(float)
        )
    except:
        group_by_categories["Amount (₹ Cr)"] = (
            group_by_categories["Amount (₹ Cr)"].astype(float)
        )
    data = (
        group_by_categories[["Category", "Amount (₹ Cr)"]]
        .rename(columns={"Category": "name", "Amount (₹ Cr)": "value"})
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
    party_left.header(f"Electoral Contributors' by Category")
    with party_left:
        st_echarts(
            options=options,
            height="600px",
        )


def top_contributors(merged_df, selected_party, party_right):

    party_n = party_right.selectbox(
        "Select Number of companies",
        [5, 10, 15, 20],
    )
    party_transactions = merged_df[merged_df["party"] == selected_party].reset_index(
        drop=True
    )
    group_by_companies = party_transactions.groupby("Company").agg(
        {"Company": "first", "Amount_y": ["sum", "count"]}
    )
    group_by_companies.columns = ["Company", "Amount", "bond_count"]
    group_by_companies["Amount (₹ Cr)"] = group_by_companies["Amount"].apply(
        format_amount
    )
    group_by_companies["percentage"] = group_by_companies["Amount"].apply(
        lambda x: calculate_percentage(x, group_by_companies["Amount"].sum())
    )
    group_by_companies = group_by_companies.sort_values("Amount", ascending=False)

    top_df = group_by_companies.head(party_n)
    others = pd.DataFrame(
        data={
            "Company": ["Other"],
            "Amount": [group_by_companies["Amount"][party_n:].sum()],
        }
    )
    others["Amount (₹ Cr)"] = (others["Amount"] / 10**7).map("{:,.2f}".format)
    combined_df = pd.concat([top_df, others])
    combined_df["Amount (₹ Cr)"] = (
        combined_df["Amount (₹ Cr)"].str.replace(",", "").astype(float)
    )
    data = (
        combined_df[["Company", "Amount (₹ Cr)"]]
        .rename(columns={"Company": "name", "Amount (₹ Cr)": "value"})
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

    with party_right:
        st_echarts(
            options=options,
            height="600px",
        )


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

    selected_party_year_spendings = party_year_group[
        party_year_group["party"] == selected_party
    ].reset_index(drop=True)
    selected_party_year_spendings["Year"] = selected_party_year_spendings[
        "Year"
    ].astype(str)
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


def display_individual_party_data(
    party_year_group, sorted_party, parties, merged_df, party_i
):
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
    party_right, party_left = party_i.columns([3, 3])
    display_donated_companies(selected_party, merged_df, party_right)
    display_donated_category(selected_party, merged_df, party_left)
    top_contributors(merged_df, selected_party, party_right)
    top_contributors_catgory(merged_df, selected_party, party_left)
    display_annual_party_contributions(party_i, party_year_group, selected_party)
    display_party_transactions(party_i, merged_df, selected_party)
