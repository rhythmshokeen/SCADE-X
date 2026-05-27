import streamlit as st
import plotly.express as px
import pandas as pd


def classify_severity(score):

    if score >= 0.75:
        return "🔴 CRITICAL"

    elif score >= 0.50:
        return "🟠 HIGH"

    elif score >= 0.20:
        return "🟡 MEDIUM"

    return "🟢 LOW"


def show_risk_panel(
    risk_df,
    raw_df
):

    st.header(
        "Risk Monitoring"
    )

    # ----------------------------------
    # Severity Classification
    # ----------------------------------

    risk_df = risk_df.copy()

    risk_df["severity"] = (
        risk_df["risk_score"]
        .apply(classify_severity)
    )

    # ----------------------------------
    # KPI Metrics
    # ----------------------------------

    total_cases = len(
        risk_df
    )

    anomalies = len(
        risk_df[
            risk_df[
                "anomaly_label"
            ] == "Anomaly"
        ]
    )

    avg_risk = round(
        risk_df[
            "risk_score"
        ].mean(),
        4
    )

    high_risk_cases = len(
        risk_df[
            risk_df[
                "risk_score"
            ] >= 0.50
        ]
    )

    highest_case = (
        risk_df.sort_values(
            "risk_score",
            ascending=False
        )
        .iloc[0][
            "case_id"
        ]
    )

    # ----------------------------------
    # Highest Risk Supplier
    # ----------------------------------

    supplier_risk_df = raw_df.merge(
        risk_df[
            [
                "case_id",
                "risk_score"
            ]
        ],
        on="case_id",
        how="left"
    )

    highest_supplier = (
        supplier_risk_df
        .groupby("supplier")[
            "risk_score"
        ]
        .mean()
        .idxmax()
    )

    anomaly_percentage = round(
        (
            anomalies
            / total_cases
        )
        * 100,
        1
    )

    # ----------------------------------
    # Executive Summary
    # ----------------------------------

    st.subheader(
        "Executive Summary"
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        st.info(
            f"""
### 🚨 System Status

**{anomaly_percentage}%**
anomalous workflows

**{high_risk_cases}**
high-risk cases
"""
        )

    with c2:
        st.info(
            f"""
### 🏭 Supplier Intelligence

Highest Risk Supplier:

**{highest_supplier}**
"""
        )

    with c3:
        st.info(
            f"""
### 🛰️ Threat Intelligence

Highest Risk Case:

**{highest_case}**

Average Risk:

**{avg_risk}**
"""
        )

    # ----------------------------------
    # KPI Cards
    # ----------------------------------

    col1, col2, col3, col4 = st.columns(
        4
    )

    col1.metric(
        "Total Cases",
        total_cases
    )

    col2.metric(
        "Detected Anomalies",
        anomalies
    )

    col3.metric(
        "Average Risk",
        avg_risk
    )

    col4.metric(
        "High Risk Cases",
        high_risk_cases
    )

    st.divider()

    # ----------------------------------
    # Main Layout
    # ----------------------------------

    left, right = st.columns(
        [1.2, 1]
    )

    # ----------------------------------
    # LEFT → Risk Distribution
    # ----------------------------------

    with left:

        st.subheader(
            "Risk Distribution"
        )

        fig = px.histogram(
            risk_df,
            x="risk_score",
            nbins=40,
            title="Risk Score Distribution"
        )

        fig.update_layout(
            height=300
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # ----------------------------------
    # RIGHT → Investigation Queue
    # ----------------------------------

    with right:

        st.subheader(
            "Investigation Queue"
        )

        merged = risk_df.merge(
            raw_df[
                [
                    "case_id",
                    "supplier",
                    "cost"
                ]
            ].drop_duplicates(),
            on="case_id",
            how="left",
            suffixes=("", "_raw")
        )

        # Handle duplicate columns safely
        if "supplier_raw" in merged.columns:
            merged["supplier"] = (
                merged["supplier_raw"]
            )

        if "cost_raw" in merged.columns:
            merged["cost"] = (
                merged["cost_raw"]
            )

        merged = merged.sort_values(
            "risk_score",
            ascending=False
        )

        merged = merged[
            [
                "case_id",
                "risk_score",
                "severity",
                "supplier",
                "cost",
                "anomaly_label"
            ]
        ]

        merged.columns = [
            "Case ID",
            "Risk Score",
            "Severity",
            "Supplier",
            "Cost",
            "Status"
        ]

        st.dataframe(
            merged.head(20),
            use_container_width=True,
            height=300
        )