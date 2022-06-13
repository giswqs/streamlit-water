import ee
import geemap.foliumap as geemap
import geemap.colormaps as cm
import geopandas as gpd
import streamlit as st

st.set_page_config(layout="wide")

# Customize the sidebar
markdown = """
Web App URL: <https://waters.streamlitapp.com>

GitHub Repository: <https://github.com/giswqs/streamlit-water>

More Apps: <https://geospatial.streamlitapp.com>

"""

st.sidebar.title("About")
st.sidebar.info(markdown)

st.sidebar.title("Contact")
st.sidebar.info(
    """
    Qiusheng Wu: <https://wetlands.io>
    [GitHub](https://github.com/giswqs) | [Twitter](https://twitter.com/giswqs) | [YouTube](https://www.youtube.com/c/QiushengWu) | [LinkedIn](https://www.linkedin.com/in/qiushengwu)
    """
)


st.title("Analyzing Global Surface Water Datasets")


@st.cache
def uploaded_file_to_gdf(data):
    import tempfile
    import os
    import uuid

    _, file_extension = os.path.splitext(data.name)
    file_id = str(uuid.uuid4())
    file_path = os.path.join(tempfile.gettempdir(), f"{file_id}{file_extension}")

    with open(file_path, "wb") as file:
        file.write(data.getbuffer())

    if file_path.lower().endswith(".kml"):
        gpd.io.file.fiona.drvsupport.supported_drivers["KML"] = "rw"
        gdf = gpd.read_file(file_path, driver="KML")
    else:
        gdf = gpd.read_file(file_path)

    return gdf


with st.expander("How to use this app"):

    markdown = """
    This interactive app allows you to explore and compare different datasets of Global Surface Water Extent (GSWE). How to use this web app?    
    - **Step 1:** Select a basemap from the dropdown menu on the right. The default basemap is `HYBRID`, a Google Satellite basemap with labels.   
    - **Step 2:** Select a region of interest (ROI) from the country dropdown menu or upload an ROI. The default ROI is the entire globe. 
    - **Step 3:** Select surface water datasets from the dropdown menu. You can select multiple datasets to display on the map.
    """
    st.markdown(markdown)

col1, col2 = st.columns([4, 1])

Map = geemap.Map(Draw_export=True, locate_control=True, plugin_LatLngPopup=True)

roi = ee.FeatureCollection("users/giswqs/public/countries")
countries = roi.aggregate_array("name").getInfo()
countries.sort()
# countries = ["United States of America"]

# lc_basemaps = [
#     "ESA Global Land Cover 2020",
#     "ESRI Global Land Cover 2020",
#     "JRC Global Surface Water",
#     "USDA NASS Cropland 2020",
#     "US NLCD 2019",
# ]

# google_basemaps = ["OpenStreetMap"] + [
#     "Google " + b for b in list(geemap.basemaps.keys())[1:5]
# ]
# basemaps = google_basemaps + lc_basemaps
basemaps = list(geemap.basemaps.keys())

with col2:

    latitude = st.number_input("Map center latitude", -90.0, 90.0, 40.0, step=0.5)
    longitude = st.number_input("Map center longitude", -180.0, 180.0, -100.0, step=0.5)
    zoom = st.slider("Map zoom level", 1, 22, 4)

    select = st.checkbox("Select a country")
    if select:
        country = st.selectbox(
            "Select a country from dropdown list",
            countries,
            index=countries.index("United States of America"),
        )
        st.session_state["ROI"] = roi.filter(ee.Filter.eq("name", country))
    else:

        with st.expander("Click here to upload an ROI", False):
            upload = st.file_uploader(
                "Upload a GeoJSON, KML or Shapefile (as a zif file) to use as an ROI. 😇👇",
                type=["geojson", "kml", "zip"],
            )

            if upload:
                gdf = uploaded_file_to_gdf(upload)
                st.session_state["ROI"] = geemap.gdf_to_ee(gdf, geodesic=False)
                # Map.add_gdf(gdf, "ROI")
            else:
                st.session_state["ROI"] = roi

    basemap = st.selectbox(
        "Select a basemap",
        basemaps,
        index=basemaps.index("HYBRID"),
    )
    Map.add_basemap(basemap)
    # if basemap in google_basemaps:
    #     Map.add_basemap(basemap.replace("Google ", ""))
    # elif basemap in lc_basemaps:

    #     if basemap == "ESA Global Land Cover 2020":
    #         dataset = ee.ImageCollection("ESA/WorldCover/v100").first()
    #         if st.session_state["ROI"] is not None:
    #             dataset = dataset.clipToCollection(st.session_state["ROI"])

    #         Map.addLayer(dataset, {}, "ESA Landcover")
    #         Map.add_legend(title="ESA Landcover", builtin_legend="ESA_WorldCover")
    #     elif basemap == "ESRI Global Land Cover 2020":

    #         esri_lulc10 = ee.ImageCollection(
    #             "projects/sat-io/open-datasets/landcover/ESRI_Global-LULC_10m"
    #         )
    #         legend_dict = {
    #             "names": [
    #                 "Water",
    #                 "Trees",
    #                 "Grass",
    #                 "Flooded Vegetation",
    #                 "Crops",
    #                 "Scrub/Shrub",
    #                 "Built Area",
    #                 "Bare Ground",
    #                 "Snow/Ice",
    #                 "Clouds",
    #             ],
    #             "colors": [
    #                 "#1A5BAB",
    #                 "#358221",
    #                 "#A7D282",
    #                 "#87D19E",
    #                 "#FFDB5C",
    #                 "#EECFA8",
    #                 "#ED022A",
    #                 "#EDE9E4",
    #                 "#F2FAFF",
    #                 "#C8C8C8",
    #             ],
    #         }

    #         vis_params = {"min": 1, "max": 10, "palette": legend_dict["colors"]}
    #         esri_lulc10 = esri_lulc10.mosaic()

    #         if st.session_state["ROI"] is not None:
    #             esri_lulc10 = esri_lulc10.clipToCollection(st.session_state["ROI"])
    #         Map.addLayer(esri_lulc10, vis_params, "ESRI Global Land Cover")
    #         Map.add_legend(title="ESRI Landcover", builtin_legend="ESRI_LandCover")

    #     elif basemap == "US NLCD 2019":
    #         nlcd = ee.Image("USGS/NLCD_RELEASES/2019_REL/NLCD/2019").select("landcover")
    #         if st.session_state["ROI"] is not None:
    #             nlcd = nlcd.clipToCollection(st.session_state["ROI"])
    #         Map.addLayer(nlcd, {}, "US NLCD 2019")
    #         Map.add_legend(title="NLCD Land Cover", builtin_legend="NLCD")

    #     elif basemap == "USDA NASS Cropland 2020":
    #         cropland = (
    #             ee.ImageCollection("USDA/NASS/CDL")
    #             .filterDate("2010-01-01", "2020-01-01")
    #             .first()
    #             .select("cropland")
    #         )

    #         if st.session_state["ROI"] is not None:
    #             cropland = cropland.clipToCollection(st.session_state["ROI"])

    #         Map.addLayer(cropland, {}, "USDA NASS Cropland 2020")

    # elif "HydroSHEDS" in datasets:
    #     hydrolakes = ee.FeatureCollection(
    #         "projects/sat-io/open-datasets/HydroLakes/lake_poly_v10"
    #     )
    #     if st.session_state["ROI"] is not None:
    #         hydrolakes = hydrolakes.filterBounds(st.session_state["ROI"])
    #     Map.addLayer(hydrolakes, {"color": "#00008B"}, "HydroSHEDS - HydroLAKES")

# roi = ee.FeatureCollection("users/giswqs/MRB/NWI_HU8_Boundary_Simplify")
style = {
    "color": "000000ff",
    "width": 1,
    "lineType": "solid",
    "fillColor": "00000000",
}

# select_holder = col2.empty()
with col2:
    datasets = st.multiselect(
        "Select surface water datasets",
        [
            "ESA Land Use",
            "JRC Max Water Extent",
            "OpenStreetMap",
            "HydroLakes",
            "LAGOS",
            "US NED Depressions",
            "Global River Width",
        ],
    )

# styles = {
#     "ESA Land Use": {
#         "color": "dca0dcff",
#         "width": width,
#         "fillColor": "e4bbe4ff",
#     },
#     "JRC Max Water Extent": {
#         "color": "ffc2cbff",
#         "width": width,
#         "fillColor": "fdd1d8ff",
#     },
#     "OpenStreetMap": {
#         "color": "bf03bfff",
#         "width": width,
#         "fillColor": "ebb2ebff",
#     },
#     "HydroLakes": {
#         "color": "4e0583ff",
#         "width": width,
#         "fillColor": "a47fbfff",
#     },
#     "LAGOS": {
#         "color": "8f228fff",
#         "width": width,
#         "fillColor": "cb99cbff",
#     },
#     "US NED Depressions": {
#         "color": "8d32e2ff",
#         "width": width,
#         "fillColor": "c394efff",
#     },
# }

width = 1
styles = {
    "ESA Land Use": {
        "color": "000000ff",
        "width": width,
        "fillColor": "dca0dcff",
    },
    "JRC Max Water Extent": {
        "color": "000000ff",
        "width": width,
        "fillColor": "ffc2cbff",
    },
    "OpenStreetMap": {
        "color": "000000ff",
        "width": width,
        "fillColor": "bf03bfff",
    },
    "HydroLakes": {
        "color": "000000ff",
        "width": width,
        "fillColor": "4e0583ff",
    },
    "LAGOS": {
        "color": "000000ff",
        "width": width,
        "fillColor": "8f228fff",
    },
    "US NED Depressions": {
        "color": "000000ff",
        "width": width,
        "fillColor": "8d32e2ff",
    },
    "Global River Width": {
        "color": "000000ff",
        "width": width,
        "fillColor": "0000ffff",
    },
}

if "ESA Land Use" in datasets:
    dataset = ee.FeatureCollection("users/giswqs/MRB/ESA_entireUS")
    Map.addLayer(dataset.style(**styles["ESA Land Use"]), {}, "ESA Land Use")

if "JRC Max Water Extent" in datasets:
    dataset = ee.FeatureCollection("users/giswqs/MRB/JRC_entireUS")
    Map.addLayer(
        dataset.style(**styles["JRC Max Water Extent"]), {}, "JRC Max Water Extent"
    )

if "OpenStreetMap" in datasets:
    dataset = ee.FeatureCollection("users/giswqs/MRB/OSM_entireUS")
    Map.addLayer(dataset.style(**styles["OpenStreetMap"]), {}, "OpenStreetMap")

if "HydroLakes" in datasets:
    dataset = ee.FeatureCollection("users/giswqs/MRB/HL_entireUS")
    Map.addLayer(dataset.style(**styles["HydroLakes"]), {}, "HydroLakes")

if "LAGOS" in datasets:
    dataset = ee.FeatureCollection("users/giswqs/MRB/LAGOS_entireUS")
    Map.addLayer(dataset.style(**styles["LAGOS"]), {}, "LAGOS")

if "US NED Depressions" in datasets:
    depressions = ee.FeatureCollection("users/giswqs/MRB/US_depressions")
    Map.addLayer(
        depressions.style(**styles["US NED Depressions"]), {}, "US NED Depressions"
    )

if datasets:
    legend_datasets = datasets[:]
    # if "Global River Width" in legend_datasets:
    #     legend_datasets.remove("Global River Width")
    legend_dict = {}
    for dataset in legend_datasets:
        legend_dict[dataset] = styles[dataset]["fillColor"][:6]

    if len(legend_datasets) > 0:

        Map.add_legend(title="Surface Water", legend_dict=legend_dict)

# if "JRC Global Surface Water" in datasets:
#     jrc = ee.Image("JRC/GSW1_3/GlobalSurfaceWater")
#     vis = {
#         "bands": ["occurrence"],
#         "min": 0.0,
#         "max": 100.0,
#         "palette": cm.palettes.coolwarm_r,
#     }
#     Map.addLayer(jrc, vis, "JRC Global Surface Water")
#     Map.add_colorbar(vis, label="Surface water occurrence (%)")

if "Global River Width" in datasets:
    water_mask = ee.ImageCollection(
        "projects/sat-io/open-datasets/GRWL/water_mask_v01_01"
    ).median()

    grwl_summary = ee.FeatureCollection(
        "projects/sat-io/open-datasets/GRWL/grwl_SummaryStats_v01_01"
    )
    grwl_water_vector = ee.FeatureCollection(
        "projects/sat-io/open-datasets/GRWL/water_vector_v01_01"
    )

    if st.session_state["ROI"] is not None:
        water_mask = water_mask.clipToCollection(st.session_state["ROI"])
        grwl_summary = grwl_summary.filterBounds(st.session_state["ROI"])

    Map.addLayer(water_mask, {"palette": "blue"}, "GRWL RIver Mask")
    Map.addLayer(
        grwl_water_vector.style(**{"fillColor": "00000000", "color": "FF5500"}),
        {},
        "GRWL Centerline",
        False,
    )
    Map.addLayer(
        grwl_summary.style(**{"fillColor": "00000000", "color": "EE5500"}),
        {},
        "GRWL Centerline Simplified",
    )

show = False
if select and country is not None:
    name = country
    style["color"] = "#000000"
    style["width"] = 2
    show = True
elif upload:
    name = "ROI"
    style["color"] = "#FFFF00"
    style["width"] = 2
    show = True
else:
    name = "World"

Map.addLayer(st.session_state["ROI"].style(**style), {}, name, show)
Map.centerObject(st.session_state["ROI"])

with col2:
    wbds = [
        "NHD-HUC2",
        "NHD-HUC4",
        "NHD-HUC6",
        "NHD-HUC8",
        "NHD-HUC10",
    ]
    wbd = st.multiselect("Select watershed boundaries", wbds)

    if "NHD-HUC2" in wbd:
        huc2 = ee.FeatureCollection("USGS/WBD/2017/HUC02")
        Map.addLayer(huc2.style(**{"fillColor": "00000000"}), {}, "NHD-HUC2")

    if "NHD-HUC4" in wbd:
        huc4 = ee.FeatureCollection("USGS/WBD/2017/HUC04")
        Map.addLayer(huc4.style(**{"fillColor": "00000000"}), {}, "NHD-HUC4")

    if "NHD-HUC6" in wbd:
        huc6 = ee.FeatureCollection("USGS/WBD/2017/HUC06")
        Map.addLayer(huc6.style(**{"fillColor": "00000000"}), {}, "NHD-HUC6")

    if "NHD-HUC8" in wbd:
        huc8 = ee.FeatureCollection("USGS/WBD/2017/HUC08")
        Map.addLayer(huc8.style(**{"fillColor": "00000000"}), {}, "NHD-HUC8")

    if "NHD-HUC10" in wbd:
        huc10 = ee.FeatureCollection("USGS/WBD/2017/HUC10")
        Map.addLayer(huc10.style(**{"fillColor": "00000000"}), {}, "NHD-HUC10")

with col1:

    if select:
        Map.centerObject(st.session_state["ROI"])
    else:
        Map.set_center(longitude, latitude, zoom)
    Map.to_streamlit(height=680)

with col2:
    with st.expander("Data Sources"):

        desc = """
            - [ESA Global Land Cover](https://developers.google.com/earth-engine/datasets/catalog/ESA_WorldCover_v100?hl=en)
            - [ESRI Global Land Cover](https://samapriya.github.io/awesome-gee-community-datasets/projects/esrilc2020/)
            - [Global River Width Dataset](https://samapriya.github.io/awesome-gee-community-datasets/projects/grwl/)
            - [JRC Global Surface Water](https://developers.google.com/earth-engine/datasets/catalog/JRC_GSW1_3_GlobalSurfaceWater)
            - [HydroSHEDS - HydroLAKES](https://samapriya.github.io/awesome-gee-community-datasets/projects/hydrolakes/)
            - [OSM Global Surface Water](https://samapriya.github.io/awesome-gee-community-datasets/projects/osm_water/)
            - [US NLCD](https://developers.google.com/earth-engine/datasets/catalog/USGS_NLCD_RELEASES_2019_REL_NLCD)
            - [US NED Depressions (10m)](https://developers.google.com/earth-engine/datasets/catalog/USGS_3DEP_10m)
            - [USDA NASS Cropland](https://developers.google.com/earth-engine/datasets/catalog/USDA_NASS_CDL)
            - [NHD Waterboday](https://samapriya.github.io/awesome-gee-community-datasets/projects/nhd)
            - [NHD-HUC2](https://developers.google.com/earth-engine/datasets/catalog/USGS_WBD_2017_HUC02)
            - [NHD-HUC4](https://developers.google.com/earth-engine/datasets/catalog/USGS_WBD_2017_HUC04)
            - [NHD-HUC6](https://developers.google.com/earth-engine/datasets/catalog/USGS_WBD_2017_HUC06)
            - [NHD-HUC8](https://developers.google.com/earth-engine/datasets/catalog/USGS_WBD_2017_HUC08)
            - [NHD-HUC10](https://developers.google.com/earth-engine/datasets/catalog/USGS_WBD_2017_HUC10)
        """
        st.markdown(desc)
