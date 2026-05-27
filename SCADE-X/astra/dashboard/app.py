import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

from components.executive_summary import (
    show_executive_summary
)

from components.workflow_analytics import (
    show_workflow_analytics
)

from components.risk_panel import (
    show_risk_panel
)

from components.root_cause_panel import (
    show_root_cause_panel
)

from components.supplier_analytics import (
    show_supplier_analytics
)

from components.workflow_explorer import (
    show_workflow_explorer
)

from components.explainability_panel import (
    show_explainability_panel
)


# ------------------------------------------------
# Page Config
# ------------------------------------------------

st.set_page_config(
    page_title="ASTRA Intelligence Dashboard",
    page_icon="🛰️",
    layout="wide"
)

# ------------------------------------------------
# Title
# ------------------------------------------------

st.title(
    "🛰️ ASTRA Intelligence Dashboard"
)

st.markdown(
    """
Advanced Supply Chain Threat
& Resilience Analytics
"""
)

# ------------------------------------------------
# Load Data
# ------------------------------------------------

risk_df = pd.read_csv(
    "data/processed/fused_risk_scores.csv"
)

raw_df = pd.read_csv(
    "data/raw/synthetic_supply_chain.csv"
)

graph_df = pd.read_csv(
    "data/processed/graph_features.csv"
)

report_path = Path(
    "data/processed/root_cause_report.txt"
)

# ------------------------------------------------
# Sidebar Navigation
# ------------------------------------------------

st.sidebar.title(
    "Navigation"
)

section = st.sidebar.radio(
    "Go To",
    [
        "Executive Intelligence",
        "Risk Monitoring",
        "Workflow Analytics",
        "Supplier Analytics",
        "Workflow Explorer",
        "Explainability"
    ]
)

# ------------------------------------------------
# Executive Intelligence
# ------------------------------------------------

if section == "Executive Intelligence":

    show_executive_summary(
        risk_df,
        raw_df
    )

# ------------------------------------------------
# Risk Monitoring
# ------------------------------------------------

elif section == "Risk Monitoring":

    show_risk_panel(
        risk_df,
        raw_df
    )

    st.divider()

    show_root_cause_panel(
        risk_df,
        raw_df
    )

# ------------------------------------------------
# Workflow Analytics
# ------------------------------------------------

elif section == "Workflow Analytics":

    show_workflow_analytics(
        raw_df,
        risk_df
    )

# ------------------------------------------------
# Supplier Analytics
# ------------------------------------------------

elif section == "Supplier Analytics":

    show_supplier_analytics(
        risk_df,
        raw_df
    )

# ------------------------------------------------
# Workflow Explorer
# ------------------------------------------------

elif section == "Workflow Explorer":

    show_workflow_explorer(
        raw_df
    )

# ------------------------------------------------
# Explainability
# ------------------------------------------------

elif section == "Explainability":

    show_explainability_panel(
        report_path
    )