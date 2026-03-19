
## Risk scores for 11 individual hazards
## for historical period and for 3 forward-looking time horizons

## description of climate scenarios is provided here : https://www.weathertrade.net/faq/scenario-analysis-is-provided-for-all-hazards-3


import os
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots

def scenario_analysis_asset_level(
    climate_risk_df,
    location_name,
    config,
    output_file="tmp/scenario_analysis_asset_level.png",
    sheet_name="data",
    show_figure=True
):
    """
    Create a 3-panel asset-level scenario analysis heatmap for one location.

    Panels:
    1. Historical + Orderly (hist + ssp126)
    2. Disorderly (ssp245)
    3. Hot-house-world (ssp585)

    Parameters
    ----------
    climate_risk_df : str
        Path to Excel file.
    location_name : str
        Asset/location name exactly as written in the Excel file.
    config : module
        Your config.py with hazard names, labels, colors, etc.
    output_file : str
        Output PNG path.
    sheet_name : str
        Excel sheet name.
    show_figure : bool
        Whether to display the figure.
    """

    df = pd.read_excel(climate_risk_df, sheet_name=sheet_name, skiprows=[0])
    df["period"] = df["period"].replace(config.period_mapping)
    df["scenario"] = df["scenario"].replace(config.scenario_mapping)
    

    # df["period"] = df["period"].astype(str).str.strip()
    # df["scenario"] = df["scenario"].astype(str).str.strip().str.lower()
    # df["location"] = df["location"].astype(str).str.strip()

    # Filter one location
    df_loc = df[df["location"] == location_name].copy()
    if df_loc.empty:
        available = sorted(df["location"].dropna().unique().tolist())
        raise ValueError(
            f"Location '{location_name}' not found. Available locations: {available}"
        )

    # Hazard codes in the desired order
    hazard_codes = [k for k in config.CHOICES_HAZARDS.keys() if k != "AL"]
    hazard_labels = [config.CHOICES_HAZARDS[h] for h in hazard_codes]

    # Panel definitions
    panel_specs = [
        {
            "title": "Historical - Orderly",
            "scenarios": ["hist", "RCP2.6"],
            "periods": ["hist", "2030", "2040", "2050"],
        },
        {
            "title": "Disorderly",
            "scenarios": ["RCP4.5"],
            "periods": ["2030", "2040", "2050"],
        },
        {
            "title": "Hot-house-world",
            "scenarios": ["RCP8.5"],
            "periods": ["2030", "2040", "2050"],
        },
    ]

    fig = make_subplots(
        rows=1,
        cols=3,
        shared_yaxes=True,
        horizontal_spacing=0.08,
        subplot_titles=[p["title"] for p in panel_specs],
    )

    for i, panel in enumerate(panel_specs, start=1):
        panel_df = df_loc[
            df_loc["scenario"].isin(panel["scenarios"]) &
            df_loc["period"].isin(panel["periods"])
        ].copy()

        # For the first panel, keep historical row for 2011-2020,
        # then use ssp126 for future periods
        if "hist" in panel["scenarios"] and "RCP2.6" in panel["scenarios"]:
            rows = []
            for period in panel["periods"]:
                if period == "hist":
                    tmp = panel_df[
                        (panel_df["period"] == period) &
                        (panel_df["scenario"] == "hist")
                    ]
                else:
                    tmp = panel_df[
                        (panel_df["period"] == period) &
                        (panel_df["scenario"] == "RCP2.6")
                    ]
                if not tmp.empty:
                    rows.append(tmp.iloc[0])

            if not rows:
                raise ValueError(f"No data found for location '{location_name}' in panel '{panel['title']}'.")

            panel_df = pd.DataFrame(rows)
        else:
            # For ssp245 / ssp585 panels, keep one row per period
            panel_df = (
                panel_df.sort_values("period")
                .drop_duplicates(subset=["period"], keep="first")
            )

        panel_df = panel_df.set_index("period").reindex(panel["periods"])

        # Build z matrix
        z = panel_df[hazard_codes].T
        z.index = hazard_labels

        # Short risk labels inside cells
        def score_to_label(x):
            if pd.isna(x):
                return ""
            if x < 0.2:
                return "L"
            elif x < 0.4:
                return "M"
            elif x < 0.6:
                return "H"
            elif x < 0.8:
                return "S"
            return "E"

        text = z.applymap(score_to_label)

        fig.add_trace(
            go.Heatmap(
                z=z.values,
                x=z.columns.tolist(),
                y=z.index.tolist(),
                text=text.values,
                texttemplate="%{text}",
                textfont={"size": 12},
                coloraxis="coloraxis",
                zmin=0,
                zmax=1,
                hovertemplate=(
                    "<b>%{y}</b><br>"
                    "Period: %{x}<br>"
                    "Risk score: %{z:.1f}<extra></extra>"
                ),
                xgap=1,
                ygap=1,
            ),
            row=1,
            col=i,
        )

    fig.update_layout(
        title=f"Risk scores scenario analysis for {location_name}",
        title_x=0.5,
        width=800,
        height=400,
        font=dict(size=13),
        paper_bgcolor="white",
        plot_bgcolor="white",
        coloraxis=dict(
            colorscale=config.wtn_colorscale_hex if hasattr(config, "wtn_colorscale_hex") else [
                [0.00, "#6f8f82"],
                [0.20, "#b8a76a"],
                [0.40, "#d18a4b"],
                [0.60, "#d84a2b"],
                [0.80, "#c81d11"],
                [1.00, "#b30000"],
            ],
            cmin=0,
            cmax=1,
            colorbar=dict(
                title="Risk levels",
                tickvals=[0.1, 0.3, 0.5, 0.7, 0.9],
                ticktext=["Low", "Moderate", "High", "Severe", "Extreme"],
                len=0.8,
            ),
        ),
        margin=dict(l=40, r=40, t=70, b=40),
    )

    fig.update_xaxes(tickangle=270)

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    pio.write_image(fig, output_file, format="png", width=800, height=400, scale=2)

    # if show_figure:
    #     fig.show()

    return fig 