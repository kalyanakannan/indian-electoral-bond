from datetime import datetime, timedelta
import urllib.parse
import pandas as pd

def format_amount(amount):
    """
    Format the amount to represent it in Crores (₹ Cr) and append the formatted string representation.

    Parameters:
    - amount: The amount in basic units to be converted and formatted.

    Returns:
    - A formatted string representing the amount in Crores with two decimal places.
    """
    return "{:,.2f}".format(amount / 10**7)

def merge_parties_companies(parties, companies):
    merged_df = pd.merge(companies, parties, on=['Bond Number', 'Prefix'])
    return merged_df


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

def aggregate_transactions(merged_df, group_by_column):
    """Aggregate transactions by a specified column."""
    transactions = merged_df.groupby(group_by_column).agg({
        group_by_column: "first",
        "Amount_y": ["sum", "count"]
    })
    transactions.columns = [group_by_column, 'Amount', 'bond_count']
    return transactions.reset_index(drop=True)

def format_and_sort_group(group, amount_format_function, percentage_calc_function):
    """Format amounts and calculate percentages, then sort."""
    group["Amount (₹ Cr)"] = group["Amount"].apply(amount_format_function)
    total_amount = group["Amount"].sum()
    group["percentage"] = group["Amount"].apply(lambda x: percentage_calc_function(x, total_amount))
    return group.sort_values("Amount", ascending=False)


def make_clickable(link, text):
    # Streamlit uses Markdown to render text, so you can use an anchor tag for the link
    return f"[{text}]({link})"

    # Adding a column to the DataFrame with the clickable links