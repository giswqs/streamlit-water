import ee
import geemap.foliumap as geemap
import geemap.colormaps as cm
import geopandas as gpd
import streamlit as st
import plotly.express as px
import leafmap

st.set_page_config(layout="wide")
geemap.ee_initialize()

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

default_vis = {
    "JRC Max Water Extent (1984-2020)": "{'min': 1, 'max': 1, 'palette': ['0000ff']}",
    "JRC Water Occurrence (1984-2020)": "{'min': 0, 'max': 100, 'palette': ['ffffff', 'ffbbbb', '0000ff']}",
    "Dynamic World 2020": "{}",
    "ESA Global Land Cover 2020": '{"bands": ["Map"]}',
    "ESRI Global Land Cover 2020": "{'min': 1, 'max': 10, 'palette': ['1A5BAB', '358221', 'A7D282', '87D19E', 'FFDB5C', 'EECFA8', 'ED022A', 'EDE9E4', 'F2FAFF', 'C8C8C8']}",
    "OpenStreetMap Water Layer": "{'min': 1, 'max': 1, 'palette': ['08306b', '08519c', '2171b5', '4292c6', '6baed6']}",
    "Global River Width (GRWL)": "{'min': 255, 'max': 255, 'palette': ['0000ff']}",
    "Global floodplains (GFPLAIN250m)": "{'palette': ['0000ff']}",
    "HydroLAKES": "{'color': '00008B'}",
}

water_vis = {
    "JRC Max Water Extent (1984-2020)": "{'min': 1, 'max': 1, 'palette': ['0000ff']}",
    "JRC Water Occurrence (1984-2020)": "{'min': 0, 'max': 100, 'palette': ['ffffff', 'ffbbbb', '0000ff']}",
    "Dynamic World 2020": "{'min': 1, 'max': 1, 'palette': ['419BDF']}",
    "ESA Global Land Cover 2020": "{'min': 1, 'max': 1, 'palette': ['0064c8']}",
    "ESRI Global Land Cover 2020": '{"min": 1, "max": 1, "palette": ["1A5BAB"]}',
    "OpenStreetMap Water Layer": "{'min': 1, 'max': 1, 'palette': ['08306b', '08519c', '2171b5', '4292c6', '6baed6']}",
    "Global River Width (GRWL)": "{'min': 255, 'max': 255, 'palette': ['0000ff']}",
    "Global floodplains (GFPLAIN250m)": "{'palette': ['0000ff']}",
    "HydroLAKES": "{'color': '00008B'}",
}


# @st.cache
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


def get_layer(dataset, vis_params, water_only, region=None, opacity=1.0):

    if isinstance(vis_params, str):
        try:
            vis_params = eval(vis_params)
        except Exception as e:
            st.error(e)
            st.error("Invalid vis params")
            vis_params = {}
    elif isinstance(vis_params, dict):
        pass
    else:
        st.error("Invalid vis params")
        vis_params = {}

    if dataset == "JRC Max Water Extent (1984-2020)":

        image = (
            ee.Image("JRC/GSW1_3/GlobalSurfaceWater").select("max_extent").selfMask()
        )

        if region is not None:
            image = image.clip(region)

        return image
    elif dataset == "JRC Water Occurrence (1984-2020)":
        image = ee.Image("JRC/GSW1_3/GlobalSurfaceWater").select("occurrence")

        if region is not None:
            image = image.clip(region)

        return image

    elif dataset == "Dynamic World 2020":
        start_date = "2020-01-01"
        end_date = "2021-01-01"
        if water_only:
            image = geemap.dynamic_world(
                region, start_date, end_date, return_type="class"
            )

            image = image.eq(0).selfMask()
        else:
            image = geemap.dynamic_world(
                region, start_date, end_date, return_type="hillshade"
            )
        if region is not None:
            image = image.clip(region)

        return image

    elif dataset == "ESA Global Land Cover 2020":
        image = ee.ImageCollection("ESA/WorldCover/v100").first()

        if water_only:
            image = image.eq(80).selfMask()

        if region is not None:
            image = image.clip(region)

        return image

    elif dataset == "ESRI Global Land Cover 2020":

        image = ee.ImageCollection(
            "projects/sat-io/open-datasets/landcover/ESRI_Global-LULC_10m"
        ).mosaic()

        if water_only:
            image = image.eq(1).selfMask()

        if region is not None:
            image = image.clip(region)

        return image

    elif dataset == "OpenStreetMap Water Layer":
        image = ee.ImageCollection(
            "projects/sat-io/open-datasets/OSM_waterLayer"
        ).mosaic()

        if region is not None:
            image = image.clip(region)

        return image

    elif dataset == "Global River Width (GRWL)":

        image = ee.ImageCollection(
            "projects/sat-io/open-datasets/GRWL/water_mask_v01_01"
        ).mosaic()

        if region is not None:
            image = image.clip(region)

        return image

    elif dataset == "Global floodplains (GFPLAIN250m)":
        image = ee.ImageCollection("projects/sat-io/open-datasets/GFPLAIN250").mosaic()

        if region is not None:
            image = image.clip(region)

        return image

    elif dataset == "HydroLAKES":
        vector = ee.FeatureCollection(
            "projects/sat-io/open-datasets/HydroLakes/lake_poly_v10"
        )

        if region is not None:
            vector = vector.filterBounds(region)

        return vector


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
basemaps = list(geemap.basemaps.keys())

with col2:

    with st.expander("Map configuration"):

        basemap = st.selectbox(
            "Select a basemap",
            basemaps,
            index=basemaps.index("HYBRID"),
        )
        Map.add_basemap(basemap)

        latitude = st.number_input("Map center latitude", -90.0, 90.0, 20.0, step=0.5)
        longitude = st.number_input(
            "Map center longitude", -180.0, 180.0, 0.0, step=0.5
        )
        zoom = st.slider("Map zoom level", 1, 22, 2)

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

    options = [
        "JRC Max Water Extent (1984-2020)",
        "JRC Water Occurrence (1984-2020)",
        "Dynamic World 2020",
        "ESA Global Land Cover 2020",
        "ESRI Global Land Cover 2020",
        "OpenStreetMap Water Layer",
        "Global River Width (GRWL)",
        "Global floodplains (GFPLAIN250m)",
        "HydroLAKES",
    ]

    water_only = st.checkbox("Show water class only", True)
    # add_legend = st.checkbox("Add legend", True)

    if water_only:
        vis_options = water_vis
    else:
        vis_options = default_vis

    with st.form("compute"):

        datasets = st.multiselect("Select datatsets to analyze", options)

        submitted = st.form_submit_button("Submit")

    # left_dataset = st.selectbox("Select a dataset for the left layer", datasets)

    # with st.expander("Vis params for the left layer"):
    #     left_params = st.text_area(
    #         "Enter vis params as a dictionary",
    #         vis_options[left_dataset],
    #     )

    # right_dataset = st.selectbox(
    #     "Select a dataset for the right layer", datasets, index=1, key="left_vis"
    # )

    # with st.expander("Vis params for the right layer"):

    #     right_params = st.text_area(
    #         "Enter vis params as a dictionary",
    #         vis_options[right_dataset],
    #         key="right_vis",
    #     )

    # left_layer = get_layer(
    #     left_dataset, left_params, water_only, st.session_state["ROI"]
    # )

    # right_layer = get_layer(
    #     right_dataset, right_params, water_only, st.session_state["ROI"]
    # )

    # Map.split_map(left_layer, right_layer)

style = {
    "color": "000000ff",
    "width": 1,
    "lineType": "solid",
    "fillColor": "00000000",
}


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

with col1:

    if select or upload:
        Map.centerObject(st.session_state["ROI"])
    else:
        Map.set_center(longitude, latitude, zoom)

    if submitted:
        for dataset in datasets:
            vis_params = eval(vis_options[dataset])
            layer = get_layer(dataset, vis_params, water_only, st.session_state["ROI"])
            Map.addLayer(layer, vis_params, dataset)

    Map.to_streamlit(height=680)

with col2:
    with st.expander("Data Sources"):

        desc = """
            - [JRC Global Surface Water](https://developers.google.com/earth-engine/datasets/catalog/JRC_GSW1_3_GlobalSurfaceWater)
            - [Dynamic World](https://dynamicworld.app)
            - [ESA Global Land Cover](https://developers.google.com/earth-engine/datasets/catalog/ESA_WorldCover_v100?hl=en)
            - [ESRI Global Land Cover](https://samapriya.github.io/awesome-gee-community-datasets/projects/esrilc2020/)
            - [OpenStreetMap Water Layer](https://samapriya.github.io/awesome-gee-community-datasets/projects/osm_water/)
            - [Global River Width](https://samapriya.github.io/awesome-gee-community-datasets/projects/grwl/)
            - [Globalfloodplains (GFPLAIN250m)](https://samapriya.github.io/awesome-gee-community-datasets/projects/gfplain250/)
            - [HydroLAKES](https://samapriya.github.io/awesome-gee-community-datasets/projects/hydrolakes/)
        """
        st.markdown(desc)

        # empty = st.empty()
        # empty.text("Computing...")

if submitted:

    # with col2:
    #     empty.text("Computing...")

    for dataset in datasets:
        # vis_params = eval(vis_options[dataset])
        # layer = get_layer(dataset, vis_params, water_only, st.session_state["ROI"])
        # Map.addLayer(layer, vis_params, dataset)

        if select or upload:
            with col2:

                region = st.session_state["ROI"]
                empty = st.empty()
                empty.text("Computing...")
                df = geemap.image_area_by_group(
                    layer,
                    region=region,
                    scale=1000,
                    denominator=1e6,
                    decimal_places=2,
                    verbose=True,
                )
                df["group"] = df.index
                df["cum_pct"] = df["percentage"].cumsum()

                fig = px.line(
                    df,
                    y="area",
                    x="group",
                    orientation="h",
                    labels={"group": "Occurrence (%)", "area": "Area (ha)"},
                )

            with col1:
                st.header(dataset)
                st.plotly_chart(fig)
                # empty.bar_chart(df["area"])
                st.dataframe(df)
                leafmap.st_download_button("Download data", df)

            with col2:
                empty.text("")

    # empty.text("")
