import pandas as pd
import plotly.express as px

def build_health_dataframe(logs):
    df = pd.DataFrame(
        logs,
        columns=[
            "BP",
            "Sugar",
            "Weight",
            "Sleep",
            "Water",
            "Steps",
            "Date"
        ]
    )

    for col in ["Sugar", "Weight", "Sleep", "Water", "Steps"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df

def create_trend_chart(df, y_col):
    fig = px.line(
        df,
        x="Date",
        y=y_col,
        title=f"{y_col} Trend"
    )
    return fig