import streamlit as st
import pandas as pd


def show_workflow_analytics(
    raw_df,
    risk_df
):

    st.header(
        "Workflow Archetype Analytics"
    )

    # ----------------------------------
    # Build workflow sequences
    # ----------------------------------

    workflows = (
        raw_df
        .sort_values(
            "timestamp"
        )
        .groupby(
            "case_id"
        )[
            "activity"
        ]
        .apply(
            lambda x:
            " → ".join(x)
        )
        .reset_index()
    )

    workflows.columns = [
        "case_id",
        "workflow"
    ]

    # ----------------------------------
    # Merge with risk
    # ----------------------------------

    merged = workflows.merge(
        risk_df[
            [
                "case_id",
                "risk_score",
                "anomaly_label"
            ]
        ],
        on="case_id"
    )

    # ----------------------------------
    # Workflow statistics
    # --------------------------------

    summary = (
        merged
        .groupby(
            "workflow"
        )
        .agg(
            frequency=(
                "case_id",
                "count"
            ),

            avg_risk=(
                "risk_score",
                "mean"
            ),

            anomaly_rate=(
                "anomaly_label",
                lambda x:
                (
                    x == "Anomaly"
                ).mean()
                * 100
            )
        )
        .reset_index()
    )

    summary[
        "avg_risk"
    ] = summary[
        "avg_risk"
    ].round(4)

    summary[
        "anomaly_rate"
    ] = summary[
        "anomaly_rate"
    ].round(1)

    summary = summary.sort_values(
        "frequency",
        ascending=False
    )

    st.subheader(
        "Top Workflow Archetypes"
    )

    st.dataframe(
        summary.head(20),
        use_container_width=True,
        height=500
    )

    st.markdown(
        """
### Why this matters

SCADE-X identifies repeated
workflow patterns and
quantifies:

- workflow frequency
- average behavioral risk
- anomaly percentage

This enables discovery of
recurrent abnormal process
archetypes in supply chains.
"""
    )
