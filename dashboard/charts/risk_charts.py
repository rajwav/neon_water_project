import plotly.express as px


def risk_distribution(df):

    data = (
        df["final_status"]
        .value_counts()
        .reset_index()
    )

    data.columns = [
        "Status",
        "Count"
    ]


    fig = px.pie(
        data,
        names="Status",
        values="Count",
        title="Water Risk Distribution",
        hole=0.45,
        color="Status",
        color_discrete_map={
            "SAFE": "green",
            "WARNING": "orange",
            "CRITICAL": "red"
        }
    )


    fig.update_layout(
        template="plotly_dark",
        height=400
    )


    return fig