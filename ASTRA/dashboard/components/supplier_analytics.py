import streamlit as st
import pandas as pd
import plotly.express as px


def show_supplier_analytics(
    risk_df,
    raw_df
):

    st.header(
        "Supplier Intelligence"
    )

    # ----------------------------------
    # Merge
    # ----------------------------------

    merged = raw_df.merge(
        risk_df[
            [
                "case_id",
                "risk_score",
                "anomaly_label"
            ]
        ],
        on="case_id",
        how="left"
    )

    # ----------------------------------
    # Supplier Metrics
    # ----------------------------------

    supplier_summary = (
        merged.groupby(
            "supplier"
        )
        .agg(
            avg_risk=(
                "risk_score",
                "mean"
            ),

            anomaly_count=(
                "anomaly_label",
                lambda x:
                (
                    x == "Anomaly"
                ).sum()
            ),

            total_cost=(
                "cost",
                "sum"
            ),

            transaction_volume=(
                "case_id",
                "nunique"
            )
        )
        .reset_index()
    )

    supplier_summary[
        "avg_risk"
    ] = supplier_summary[
        "avg_risk"
    ].round(4)

    supplier_summary = (
        supplier_summary
        .sort_values(
            "avg_risk",
            ascending=False
        )
    )

    # ----------------------------------
    # Executive View
    # ----------------------------------

    st.subheader(
        "Supplier Risk Overview"
    )

    fig = px.imshow(
        supplier_summary.set_index(
            "supplier"
        )[
            [
                "avg_risk",
                "anomaly_count",
                "total_cost",
                "transaction_volume"
            ]
        ],
        text_auto=True,
        aspect="auto",
        title="Supplier Risk Heatmap"
    )

    fig.update_layout(
        height=400
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # ----------------------------------
    # Supplier Ranking
    # ----------------------------------

    st.subheader(
        "Supplier Intelligence Table"
    )

    st.dataframe(
        supplier_summary,
        use_container_width=True,
        height=400
    )

    # ----------------------------------
    # Key Findings
    # ----------------------------------

    top_supplier = (
        supplier_summary
        .iloc[0][
            "supplier"
        ]
    )

    st.info(
        f"""
### Key Intelligence

• Highest risk supplier:
**{top_supplier}**

• SCADE-X evaluates supplier
risk using:

- behavioral anomaly rate
- process anomalies
- cost exposure
- transaction volume
"""
    )