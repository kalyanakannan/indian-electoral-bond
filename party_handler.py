import matplotlib.pyplot as plt
import pandas as pd

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