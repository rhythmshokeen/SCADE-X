import streamlit as st


def show_explainability_panel(
    report_path
):

    st.header(
        "Explainability Report"
    )

    st.markdown(
        """
        This section displays
        SCADE-X's generated
        root cause analysis
        and explainability report.
        """
    )

    if report_path.exists():

        with open(
            report_path,
            "r"
        ) as f:

            report = f.read()

        st.text_area(
            "Root Cause Report",
            report,
            height=700
        )

    else:

        st.error(
            "Explainability report not found."
        )