import streamlit as st
import pandas as pd
import plotly.express as px


def show_workflow_explorer(
    raw_df
):

    st.header(
        "Workflow Explorer"
    )

    workflows = (
        raw_df.groupby(
            "case_id"
        )["activity"]
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

    workflow_counts = (
        workflows[
            "workflow"
        ]
        .value_counts()
        .reset_index()
    )

    workflow_counts.columns = [
        "workflow",
        "count"
    ]

    st.subheader(
        "Most Common Workflow Patterns"
    )

    fig = px.bar(
        workflow_counts.head(15),
        x="count",
        y="workflow",
        orientation="h",
        title=(
            "Most Frequent "
            "Workflow Sequences"
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.subheader(
        "Workflow Frequency Table"
    )

    st.dataframe(
        workflow_counts,
        use_container_width=True
    )

    st.subheader(
        "Inspect Specific Workflow"
    )

    case_ids = workflows[
        "case_id"
    ].tolist()

    selected_case = st.selectbox(
        "Select Case",
        case_ids
    )

    selected_workflow = (
        workflows[
            workflows[
                "case_id"
            ]
            ==
            selected_case
        ][
            "workflow"
        ]
        .iloc[0]
    )

    st.info(
        selected_workflow
    )