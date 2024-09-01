#!/usr/bin/env python
# coding: utf-8

"""
Slain police officers locations
This script processes the locations of line-of-duty deaths 
among American police officers from a lat/lon associated with 
each case and then assigns countries. It also plots maps of locations
within the continental United States and exports maps for a few specific
causes, such as gunfire or terrorist attacks.
"""

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

# CASES

# Import archive
archive_src = pd.read_json(
    "https://stilesdata.com/police-end-of-watch/us_slain_police_officers_archive_1900_present.json"
)

# Filter out rows where lat or lon is null or zero
archive_filtered = archive_src.dropna(subset=["lat", "lon"])
archive_clean = archive_filtered[
    (archive_filtered["lat"] != 0.0) & (archive_filtered["lon"] != 0.0)
]

# GEOGRAPHY
# World countries
country_boundaries_gdf = gpd.read_file("data/geo/countries_simple.json")
# USA lower 48 boundary
usa_conus_boundaries_gdf = gpd.read_file(
    "data/geo/usa_boundaries_lakes_conus.geojson"
)
# State boundaries
states_gdf = gpd.read_file("data/geo/usa_states_no_lakes.geojson").query(
    '~state_name.isin(["Hawaii", "Alaska"])'
)

# Create geodataframe of cases based on provided lat/lon
archive_gdf = gpd.GeoDataFrame(
    archive_clean,
    geometry=gpd.points_from_xy(archive_clean.lon, archive_clean.lat),
    crs="EPSG:4326",
)

# Perform a spatial join to assign the country ("ADMIN" and "ISO_A3") to each case
archive_with_country_gdf = gpd.sjoin(
    archive_gdf,
    country_boundaries_gdf[["ADMIN", "ISO_A3", "geometry"]],
    how="left",
    predicate="intersects",
)

# Clip the GeoDataFrame to the Continental United States
conus_archive_gdf = gpd.clip(archive_with_country_gdf, states_gdf)

# Define the Albers Equal-Area projection (EPSG:5070)
albers_projection = "EPSG:5070"

# Reproject the GeoDataFrame to Albers Equal-Area
conus_archive_gdf_albers = conus_archive_gdf.to_crs(albers_projection)
# Reproject the GeoDataFrame to Albers Equal-Area
states_gdf_albers = states_gdf.to_crs(albers_projection)

selected_causes = [
    "Gunfire",
    "COVID19",
    "Automobile crash",
    "Terrorist attack",
    "Aircraft accident",
]

causes = list(conus_archive_gdf_albers.cause.unique())

# Loop through each cause, filter the GeoDataFrame, and plot
for cause in selected_causes:
    # Filter the GeoDataFrame based on the cause
    cause_gdf = conus_archive_gdf_albers[conus_archive_gdf_albers.cause == cause]

    # Create the plot
    fig, ax = plt.subplots(figsize=(12, 10))

    # Plot the states with a faint light gray fill and dark gray thin boundaries
    states_gdf_albers.plot(
        ax=ax, facecolor="#f0f0f0", edgecolor="darkgray", linewidth=0.5
    )

    # Plot the points with the specified cause
    cause_gdf.plot(ax=ax, markersize=1, color="#374f6b", alpha=0.2)

    # Set the title with the desired font properties
    ax.set_title(
        f"Fallen officer locations, 1900-present: {cause}",
        fontsize=16,
        fontweight="bold",
        fontname="DejaVu Sans",
        # color="#374f6b",
        loc="center",
    )

    # Remove the axes for a cleaner look
    ax.set_axis_off()

    # Save the plot as a PNG file, using the cause in the filename
    plt.savefig(
        f'visuals/fallen_officer_locations_{cause.lower().replace(" ", "_")}.png',
        dpi=300,
        bbox_inches="tight",
        pad_inches=0.1,
    )

    # Optionally, display the plot
    plt.show()

    # Close the figure to free up memory
    plt.close(fig)
    
archive_with_country_gdf['date'] = archive_with_country_gdf['date'].astype(str)
archive_with_country_gdf.to_file(
    "data/processed/us_slain_police_officers_archive_1900_present.geojson",
    driver="GeoJSON",
)