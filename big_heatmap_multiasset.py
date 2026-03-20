
## data : risk scores [0 to 1 scale]
## input file : Excel in /tmp folder here (with one spreadsheet)
## if there are more than 50 locations in the input file, then we only include the first 50 locations
## default: historical period

## this BIG heatmap compares risk score values between locations


import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

def big_heatmap_multiasset(climate_risk_df,
    config,
    output_file="tmp/heatmap_compare_all_hazards_all_locations.png",
    sheet_name="data",
    period="hist",
    show_figure=True
):
    df = pd.read_excel(climate_risk_df, sheet_name=sheet_name, skiprows=[0])

    df["period"] = df["period"].replace(config.period_mapping)

    filtered_df = df[(df["period"] == "hist")].copy()
    title_suffix = "historical period"

    hazard_codes = [key for key in config.CHOICES_HAZARDS.keys() if key in filtered_df.columns]

    melted = filtered_df.melt(
        id_vars=["location"],
        value_vars=hazard_codes,
        var_name="hazard",
        value_name="value"
    )

    melted["hazard"] = melted["hazard"].map(config.CHOICES_HAZARDS)

    heatmap_data = melted.pivot_table(
        index="hazard",
        columns="location",
        values="value"
    )

    # STRICT hazard order from config (excluding AL)
    hazard_codes = [k for k in config.CHOICES_HAZARDS.keys() if k != "AL"]
    
    hazard_labels = [config.CHOICES_HAZARDS[h] for h in hazard_codes]
    
    # Ensure ALL hazards exist (important)
    for h in hazard_labels:
        if h not in heatmap_data.index:
            heatmap_data.loc[h] = None
    
    # Reorder strictly
    heatmap_data = heatmap_data.reindex(index=hazard_labels)
    
    # IMPORTANT: reverse so first appears at TOP
    heatmap_data = heatmap_data.iloc[::-1]

    cmap = mcolors.ListedColormap(config.clrs)
    c_ticks = [(config.bins[i] + config.bins[i + 1]) / 2 for i in range(len(config.bins) - 1)]
    norm = mcolors.BoundaryNorm(config.bins, cmap.N)

    plt.figure(figsize=(20, 7))
    sns.set(style="whitegrid")

    ax = sns.heatmap(
        heatmap_data,
        cmap=cmap,
        norm=norm,
        vmin=0,
        vmax=1,
        linewidths=0.8,
        linecolor="white",
        cbar_kws={
            "ticks": c_ticks,
            "format": "%.2f",
            "pad": 0.01,
        }
    )

    colorbar = ax.collections[0].colorbar
    colorbar.set_ticklabels(config.labels)
    colorbar.ax.tick_params(labelsize=16)

    plt.title(f"Climate Risk Scores by facility, {title_suffix}", fontsize=18, pad=20)
    plt.xlabel("Locations", fontsize=16)
    plt.ylabel("Hazard type", fontsize=16)
    plt.xticks(rotation=50, ha="right", fontsize=14)
    plt.yticks(rotation=0, fontsize=14)
    plt.tight_layout()

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    plt.savefig(output_file, dpi=300, bbox_inches="tight")

    if show_figure:
        plt.show()
    else:
        plt.close()

    # return heatmap_data
    return plt