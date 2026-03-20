import os
import config

# Imports for visualisations
from dynamic_html_map import dynamic_html_map
from piecharts_top2_hazards import piecharts_top2_hazards
from big_heatmap_multiasset import big_heatmap_multiasset
from scenario_analysis_asset_level import scenario_analysis_asset_level


def main():
    # -----------------------------
    # INPUT FILES
    # -----------------------------
    my_locations_file = 'data_samples/asset_geocoordinates.csv'
    reference_column = 'id'

    climate_risk_df = 'data_samples/wtn_risk_score_example_data_18_locations.xlsx'

    output_dir = "tmp"
    os.makedirs(output_dir, exist_ok=True)

    # -----------------------------
    # STEP 1: Map of locations
    # -----------------------------
    print("Step 1: Generating map...")
    # dynamic_html_map(my_locations_file, reference_column)

    # -----------------------------
    # STEP 2: Top hazards (piecharts)
    # -----------------------------
    print("Step 2: Generating pie charts...")
    # fig, top_hazards, pie_data = piecharts_top2_hazards(climate_risk_df, config)

    # -----------------------------
    # STEP 3: Multi-asset heatmap
    # -----------------------------
    print("Step 3: Generating portfolio heatmap...")
    big_heatmap_multiasset(
        climate_risk_df=climate_risk_df,
        config=config
    )

    # -----------------------------
    # STEP 4: Asset-level scenario analysis
    # -----------------------------
    print("Step 4: Generating asset-level scenario analysis...")
    scenario_analysis_asset_level(
        climate_risk_df=climate_risk_df,
        location_name="Taixing",
        config=config,
        output_file=os.path.join(output_dir, "scenario_analysis_taixing.png")
    )

    print("All done.")


if __name__ == "__main__":
    main()