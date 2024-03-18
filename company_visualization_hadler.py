import urllib.parse
import matplotlib.pyplot as plt
import pandas as pd
from streamlit_echarts import st_echarts
import streamlit as st

def bond_purchase_heatmap(company_ov_vi, companies):
    Years = companies['Year'].drop_duplicates().sort_values().tolist()
    months = companies['Month'].drop_duplicates().sort_values().tolist()
    print(Years)
    print(months)

    transaction_counts = companies.groupby(['Year', 'Month']).size().reset_index(name='transactions')
    

    # Pivot to get a matrix format suitable for a heatmap
    transaction_matrix = transaction_counts.pivot_table(values='transactions', index='Year', columns='Month', fill_value=0)
    
    # Ensure the months are in the correct order
    months_ordered = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    transaction_matrix = transaction_matrix.reindex(columns=months_ordered)
    
    transaction_matrix.fillna(0, inplace=True)
    
    data_for_heatmap = [
        [month, str(year), int(transaction_matrix.loc[year, month])]
        for year in transaction_matrix.index
        for month in transaction_matrix.columns
    ]

    # data_for_heatmap = [[d[1], d[0], d[2] if d[2] != 0 else "-"] for d in data_for_heatmap]

    data_for_heatmap = [
        [str(year), str(month), transaction_count]
        for year, month, transaction_count in data_for_heatmap
        if transaction_count != 0  # Exclude zero counts
    ]

    max_count = max(count for _, _, count in data_for_heatmap if count is not None)

    option = {
        "tooltip": {"position": "top"},
        "grid": {"height": "50%", "top": "10%"},
        "xAxis": {"type": "category", "data": months_ordered, "splitArea": {"show": True}},
        "yAxis": {"type": "category", "data": Years, "splitArea": {"show": True}},
        "visualMap": {
            "min": 1,
            "max": max_count,
            "calculable": True,
            "orient": "horizontal",
            "left": "center",
            "bottom": "15%",
        },
        "series": [
            {
                "name": "Bonds Purchased",
                "type": "heatmap",
                "data": data_for_heatmap,
                "label": {"show": True},
                "emphasis": {
                    "itemStyle": {"shadowBlur": max_count, "shadowColor": "rgba(0, 0, 0, 0.5)"}
                },
            }
        ],
    }
    company_ov_vi.header("Annual Trends in Corporate Electoral Bond Investments")
    with company_ov_vi:
        st_echarts(option, height="500px")

def top_category(company_ov_vi, category_group, n, left_Col):
    top_5_df = category_group.head(n)
    top_5_df["Amount (₹ Cr)"] = top_5_df["Amount (₹ Cr)"].str.replace(",", "").astype(float)
    data = (
        top_5_df[["Category", "Amount (₹ Cr)"]]
        .rename(columns={"Category": "name", "Amount (₹ Cr)": "value"})
        .to_dict("records")
    )
    print(data)
    category_options = {
       
        "tooltip": {"trigger": "item"},
        "legend": {"orient": "vertical", "left": "left"},
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
    left_Col.header(f"Top {n} Contribution Categories: Distribution of Shares")
    with company_ov_vi:
        with left_Col:
            st_echarts(
                options=category_options,
                height="600px",
            )


def top_contributors(company_ov_vi, sorted_company, n, right_col):
    top_5_df = sorted_company.head(n)
    others = pd.DataFrame(
        data={"Company": ["Other"], "Amount": [sorted_company["Amount"][n:].sum()]}
    )
    others["Amount (₹ Cr)"] = (others["Amount"] / 10**7).map("{:,.2f}".format)
    combined_df = pd.concat([top_5_df, others])
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
    right_col.header(f"Top {n} Electoral Contributors' Share in Total Contributions")
    with company_ov_vi:
        with right_col:
            st_echarts(
                options=options,
                height="600px",
            )


def display_overall_company_visualization(
    sorted_company, parent_company_group, category_group, companies, company_ov_vi
):
    n = company_ov_vi.selectbox(
            "Select Number of Entries to Display", [5,10,15,20]
        )
    right_col, left_Col = company_ov_vi.columns([3,3])
    right_col.markdown(" <style>iframe{ height: 500px !important } ", unsafe_allow_html=True)
    left_Col.markdown(" <style>iframe{ height: 500px !important } ", unsafe_allow_html=True)
    top_contributors(company_ov_vi, sorted_company, n, right_col)
    top_category(company_ov_vi, category_group, n, left_Col)
    bond_purchase_heatmap(company_ov_vi, companies)
