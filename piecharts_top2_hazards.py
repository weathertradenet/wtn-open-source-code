
## 4 piecharts (2 x 2)
## TWO hazards are selected using MAX asset-level risk score values (historical period)
## you can propose your own way to select the "most important hazards" for a group of locations

import os
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio

def prepare_pie_data(df_long, hazard, period, scenario, bins, labels):
    subset = df_long[
        (df_long["hazard"] == hazard)
        & (df_long["period"] == period)
        & (df_long["scenario"] == scenario)
    ]
    categories = pd.cut(
        subset["risk_score"],
        bins=bins,
        labels=labels,
        include_lowest=True
    )
    counts = categories.value_counts().reindex(labels, fill_value=0)
    return counts


def load_and_prepare_climate_data(climate_risk_df, config, sheet_name="data"):
    df = pd.read_excel(climate_risk_df, sheet_name=sheet_name, skiprows=[0])

    df["period"] = df["period"].replace(config.period_mapping)
    df["scenario"] = df["scenario"].replace(config.scenario_mapping)

    df_long = df.melt(
        id_vars=["location", "period", "scenario"],
        value_vars=["CS", "HW", "LS", "WF", "DR", "SS", "ER", "TC", "PC", "SL", "FD"],
        var_name="hazard",
        value_name="risk_score"
    )

    return df, df_long


def get_top_2_hazards(df, config):
    hazard_cols = [col for col in config.CHOICES_HAZARDS if col != "AL"]

    df_hist = df[df["scenario"] == "hist"].copy()
    if df_hist.empty:
        raise ValueError("No historical data found after scenario mapping.")

    max_values = df_hist[hazard_cols].max().sort_values(ascending=False)
    top_hazards = max_values.head(2).index.tolist()

    if len(top_hazards) < 2:
        raise ValueError("Not enough hazards found to build the chart.")

    return top_hazards


def build_pie_data(df_long, top_hazards, left_period, right_period, config):
    hazard1, hazard2 = top_hazards

    pie_data = {
        "hazard1_left": prepare_pie_data(df_long, hazard1, *left_period, config.bins, config.labels),
        "hazard1_right": prepare_pie_data(df_long, hazard1, *right_period, config.bins, config.labels),
        "hazard2_left": prepare_pie_data(df_long, hazard2, *left_period, config.bins, config.labels),
        "hazard2_right": prepare_pie_data(df_long, hazard2, *right_period, config.bins, config.labels),
    }

    return pie_data


def create_top2_hazards_piechart_figure(
    pie_data,
    top_hazards,
    config,
    target_year="2050",
    scenario_name="RCP8.5"
):
    hazard1, hazard2 = top_hazards

    fig = make_subplots(
        rows=2,
        cols=2,
        specs=[
            [{"type": "domain"}, {"type": "domain"}],
            [{"type": "domain"}, {"type": "domain"}]
        ],
        horizontal_spacing=0.25,
        vertical_spacing=0.1
    )

    plots_info = [
        (1, 1, pie_data["hazard1_left"],  f"{config.CHOICES_HAZARDS[hazard1]}<br><br>Historical"),
        (1, 2, pie_data["hazard1_right"], f"{config.CHOICES_HAZARDS[hazard1]}<br><br>{target_year} <br> {scenario_name}"),
        (2, 1, pie_data["hazard2_left"],  f"{config.CHOICES_HAZARDS[hazard2]}<br><br>Historical"),
        (2, 2, pie_data["hazard2_right"], f"{config.CHOICES_HAZARDS[hazard2]}<br><br>{target_year} <br> {scenario_name}")
    ]

    for row, col, data, title in plots_info:
        filtered_labels = [label for label, value in zip(config.labels, data) if value > 0]
        filtered_values = [value for value in data if value > 0]
        filtered_colors = [
            color for label, color, value in zip(config.labels, config.clrs, data) if value > 0
        ]

        fig.add_trace(
            go.Pie(
                labels=filtered_labels,
                values=filtered_values,
                hole=0.77,
                marker_colors=filtered_colors,
                sort=False,
                textinfo="none",
                texttemplate="%{label}<br>%{percent:.0%}",
                hovertemplate="%{label}: %{percent:.0%}<extra></extra>",
                textfont_size=14
            ),
            row=row,
            col=col
        )

    for i, (_, _, _, title) in enumerate(plots_info):
        domain = fig.data[i].domain
        x_center = (domain["x"][0] + domain["x"][1]) / 2
        y_center = (domain["y"][0] + domain["y"][1]) / 2

        fig.add_annotation(
            text=title,
            x=x_center,
            y=y_center,
            font=dict(size=14, family="Arial", color="black"),
            showarrow=False,
            xanchor="center",
            yanchor="middle"
        )

    fig.update_layout(
        height=600,
        width=600,
        margin=dict(t=20, b=20, l=30, r=30),
        showlegend=False
    )

    return fig


def piecharts_top2_hazards(
    climate_risk_df,
    config,
    output_file="tmp/piecharts_top2_hazards.png",
    sheet_name="data",
    left_period=("hist", "hist"),
    right_period=("2050", "RCP8.5"),
    target_year="2050",
    scenario_name="RCP8.5",
    show_figure=True
):
    df, df_long = load_and_prepare_climate_data(climate_risk_df, config, sheet_name=sheet_name)
    top_hazards = get_top_2_hazards(df, config)
    pie_data = build_pie_data(df_long, top_hazards, left_period, right_period, config)

    fig = create_top2_hazards_piechart_figure(
        pie_data=pie_data,
        top_hazards=top_hazards,
        config=config,
        target_year=target_year,
        scenario_name=scenario_name
    )

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    pio.write_image(fig, output_file, format="png", width=600, height=600, scale=2)

    if show_figure:
        fig.show()

    return fig, top_hazards, pie_data