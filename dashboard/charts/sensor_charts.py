import plotly.express as px


def sensor_line_chart(df, sensor, title):

    fig = px.line(
        df,
        x="timestamp",
        y=sensor,
        title=title
    )

    fig.update_layout(
        template="plotly_dark",
        height=350
    )

    return fig



def anomaly_chart(df):

    fig = px.scatter(
        df,
        x="timestamp",
        y="pH",
        color="anomaly_status",
        title="AI Anomaly Detection Timeline",
        color_discrete_map={
            1: "green",
            -1: "red"
        }
    )

    fig.update_layout(
        template="plotly_dark",
        height=400
    )

    return fig