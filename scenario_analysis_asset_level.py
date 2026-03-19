
## Risk scores for 11 individual hazards
## for historical period and for 3 forward-looking time horizons

## description of climate scenarios is provided here : https://www.weathertrade.net/faq/scenario-analysis-is-provided-for-all-hazards-3


import os
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots


def build_discrete_plotly_colorscale(bins, colors):
    zmin = bins[0]
    zmax = bins[-1]
    span = zmax - zmin

    colorscale = []
    for i, color in enumerate(colors):
        left = (bins[i] - zmin) / span
        right = (bins[i + 1] - zmin) / span
        colorscale.append([left, color])
        colorscale.append([right, color])

    return colorscale


def scenario_analysis_asset_level(
    climate_risk_df,
    location_name,
    config,
    output_file="tmp/scenario_analysis_asset_level.png",
    sheet_name="data",
    show_figure=True
):

    df = pd.read_excel(climate_risk_df, sheet_name=sheet_name, skiprows=[0])

    # Apply mappings for display
    df["period"] = df["period"].replace(config.period_mapping)
    df["scenario"] = df["scenario"].replace(config.scenario_mapping)
    df["location"] = df["location"].astype(str).str.strip()

    df_loc = df[df["location"] == location_name].copy()
    if df_loc.empty:
        raise ValueError(f"Location '{location_name}' not found")

    # Hazard order from config (STRICT)
    hazard_codes = [k for k in config.CHOICES_HAZARDS.keys() if k != "AL"]

    # Panels
    panel_specs = [
        {
            "title": "Historical - Orderly",
            "periods": ["hist", "2030", "2040", "2050"],
            "scenario_by_period": {
                "hist": "hist",
                "2030": "RCP2.6",
                "2040": "RCP2.6",
                "2050": "RCP2.6",
            },
        },
        {
            "title": "Disorderly",
            "periods": ["2030", "2040", "2050"],
            "scenario": "RCP4.5",
        },
        {
            "title": "Hot-house-world",
            "periods": ["2030", "2040", "2050"],
            "scenario": "RCP8.5",
        },
    ]

    fig = make_subplots(
        rows=1,
        cols=3,
        shared_yaxes=True,
        horizontal_spacing=0.08,
        subplot_titles=[p["title"] for p in panel_specs],
        column_widths=[1.25, 1, 1]
    )

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

    for i, panel in enumerate(panel_specs, start=1):

        if i == 1:
            rows = []
            for period in panel["periods"]:
                scenario = panel["scenario_by_period"][period]
                tmp = df_loc[
                    (df_loc["period"] == period) &
                    (df_loc["scenario"] == scenario)
                ]
                if not tmp.empty:
                    rows.append(tmp.iloc[0])

            panel_df = pd.DataFrame(rows)

        else:
            panel_df = df_loc[
                (df_loc["scenario"] == panel["scenario"]) &
                (df_loc["period"].isin(panel["periods"]))
            ].copy()

            panel_df = (
                panel_df.sort_values("period")
                .drop_duplicates(subset=["period"], keep="first")
            )

        panel_df = panel_df.set_index("period").reindex(panel["periods"])

        # enforce full hazard order (even if some are missing)
        z = panel_df.copy()
        
        # ensure ALL hazard columns exist
        for h in hazard_codes:
            if h not in z.columns:
                z[h] = None
        
        # now reorder strictly
        z = z[hazard_codes].T
        
        # map labels AFTER ordering
        z.index = [config.CHOICES_HAZARDS[h] for h in hazard_codes]

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
                xgap=2,
                ygap=2,
            ),
            row=1,
            col=i,
        )

    # ✅ DISCRETE COLORS from config
    colorscale = build_discrete_plotly_colorscale(config.bins, config.clrs)

    fig.update_layout(
        title=f"Risk scores scenario analysis for {location_name}",
        title_x=0.5,
        width=800,
        height=400,
        font=dict(size=13),
        paper_bgcolor="white",
        plot_bgcolor="white",
        coloraxis=dict(
            colorscale=colorscale,
            cmin=0,
            cmax=1,
            colorbar=dict(
                title="Risk levels",
                tickvals=[
                    (config.bins[i] + config.bins[i + 1]) / 2
                    for i in range(len(config.bins) - 1)
                ],
                ticktext=config.labels,
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