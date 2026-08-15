import streamlit as st


def water_alert(status, message):

    if status == "SAFE":

        st.success(
            f"🟢 {message}"
        )

    elif status == "WARNING":

        st.warning(
            f"🟡 {message}"
        )

    else:

        st.error(
            f"🔴 {message}"
        )