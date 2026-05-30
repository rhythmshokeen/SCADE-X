import streamlit as st
import pandas as pd


def show_executive_summary(
    risk_df,
    raw_df
):

    st.header(
        "Executive Intelligence"
    )

    # ----------------------------------
    # Metrics
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

    anomaly_pct = round(
        (
            anomalies
            / total_cases
        )
        * 100,
        1
    )

    avg_risk = round(
        risk_df[
            "risk_score"
        ].mean(),
        4
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
    # Supplier intelligence
    # ----------------------------------

    supplier_df = raw_df.merge(
        risk_df[
            [
                "case_id",
                "risk_score"
            ]
        ],
        on="case_id"
    )

    highest_supplier = (
        supplier_df
        .groupby(
            "supplier"
        )[
            "risk_score"
        ]
        .mean()
        .idxmax()
    )

    # ----------------------------------
    # Most common anomaly
    # ----------------------------------

    anomaly_name = (
        raw_df[
            raw_df[
                "true_anomaly"
            ]
            == True
        ][
            "anomaly_type"
        ]
        .mode()
        .iloc[0]
    )

    # ----------------------------------
    # Threat level
    # ----------------------------------

    if avg_risk >= 0.50:
        threat_level = (
            "🔴 CRITICAL"
        )

    elif avg_risk >= 0.25:
        threat_level = (
            "🟠 ELEVATED"
        )

    else:
        threat_level = (
            "🟢 STABLE"
        )

    # ----------------------------------
    # Layout
    # ----------------------------------

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Workflows Analyzed",
        total_cases
    )

    c2.metric(
        "Anomalous Workflows",
        f"{anomaly_pct}%"
    )

    c3.metric(
        "Average Risk",
        avg_risk
    )

    st.info(
        f"""
### SCADE-X Executive Assessment

**Threat Level:** {threat_level}

**Highest Risk Supplier:** {highest_supplier}

**Most Common Threat:** {anomaly_name}

**Highest Risk Case:** {highest_case}

**Average System Risk:** {avg_risk}
"""
    )
    