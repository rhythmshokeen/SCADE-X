import streamlit as st


def classify_severity(score):

    if score >= 0.75:
        return "🔴 CRITICAL"

    elif score >= 0.50:
        return "🟠 HIGH"

    elif score >= 0.20:
        return "🟡 MEDIUM"

    return "🟢 LOW"


def show_root_cause_panel(
    risk_df,
    raw_df
):

    st.header(
        "Root Cause Explorer"
    )

    case_ids = (
        risk_df[
            "case_id"
        ]
        .tolist()
    )

    selected_case = st.selectbox(
        "Select Case ID",
        case_ids
    )

    case_risk = risk_df[
        risk_df[
            "case_id"
        ]
        ==
        selected_case
    ].iloc[0]

    case_df = raw_df[
        raw_df[
            "case_id"
        ]
        ==
        selected_case
    ]

    workflow = (
        case_df[
            "activity"
        ]
        .tolist()
    )

    cost = (
        case_df[
            "cost"
        ]
        .iloc[0]
    )

    risk_score = round(
        case_risk[
            "risk_score"
        ],
        4
    )

    severity = classify_severity(
        risk_score
    )

    findings = []

    # ----------------------------------
    # Rule-based findings
    # ----------------------------------

    if (
        case_risk[
            "behavioral_anomaly_score"
        ]
        > 0.15
    ):
        findings.append(
            "⚠ High behavioral anomaly detected"
        )

    if (
        case_risk[
            "anomaly_label"
        ]
        == "Anomaly"
    ):
        findings.append(
            "⚠ Isolation Forest anomaly detected"
        )

    if (
        "APPROVE_PO"
        not in workflow
    ):
        findings.append(
            "⚠ Approval step missing"
        )

    if (
        "INVENTORY_UPDATED"
        not in workflow
    ):
        findings.append(
            "⚠ Inventory update missing"
        )

    if (
        workflow.count(
            "APPROVE_PO"
        ) > 1
    ):
        findings.append(
            "⚠ Duplicate approval detected"
        )

    if (
        "PAYMENT_COMPLETED"
        in workflow
        and
        "SHIPMENT_CREATED"
        in workflow
    ):

        payment_idx = workflow.index(
            "PAYMENT_COMPLETED"
        )

        shipment_idx = workflow.index(
            "SHIPMENT_CREATED"
        )

        if payment_idx < shipment_idx:

            findings.append(
                "⚠ Payment occurred before shipment"
            )

    if cost > 15000:

        findings.append(
            "⚠ High transaction cost"
        )

    # ----------------------------------
    # Intelligence Layout
    # ----------------------------------

    st.subheader(
        f"Case Intelligence: {selected_case}"
    )

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Risk Score",
        risk_score
    )

    c2.metric(
        "Severity",
        severity
    )

    c3.metric(
        "Transaction Cost",
        f"₹{cost:,.0f}"
    )

    st.markdown(
        "### Workflow Sequence"
    )

    st.info(
        " → ".join(
            workflow
        )
    )

    st.markdown(
        "### Detected Problems"
    )

    if findings:

        for finding in findings:

            st.warning(
                finding
            )

    else:

        st.success(
            "No abnormal signals detected."
        )

    st.markdown(
        "### Recommended Attention"
    )

    if risk_score >= 0.75:

        st.error(
            "Immediate investigation required."
        )

    elif risk_score >= 0.50:

        st.warning(
            "Monitor closely."
        )

    else:

        st.success(
            "Low operational concern."
        )