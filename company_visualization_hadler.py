import urllib.parse
import matplotlib.pyplot as plt
import pandas as pd
from streamlit_echarts import st_echarts
import streamlit as st

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
    sorted_company, parent_company_group, category_group, company_ov_vi
):
    n = company_ov_vi.selectbox(
            "Select Number of Entries to Display", [5,10,15,20]
        )
    right_col, left_Col = company_ov_vi.columns([3,3])
    right_col.markdown(" <style>iframe{ height: 500px !important } ", unsafe_allow_html=True)
    left_Col.markdown(" <style>iframe{ height: 500px !important } ", unsafe_allow_html=True)
    top_contributors(company_ov_vi, sorted_company, n, right_col)
    top_category(company_ov_vi, category_group, n, left_Col)
