import streamlit as st


def metric_card(title, value, icon="📊"):

    st.metric(
        label=f"{icon} {title}",
        value=value
    )