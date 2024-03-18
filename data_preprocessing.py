from utils import aggregate_data

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

