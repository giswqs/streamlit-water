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


st.title("Visualizing Global Surface Water Datasets")


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

    datasets = [
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

    dataset = st.selectbox("Select a water dataset", datasets)

    with st.expander("Set visualization parameters"):
        params_input = st.empty()
        opacity = st.slider("Set layer opacity", 0.0, 1.0, 1.0)

    water_only = st.checkbox("Show water class only")
    split = st.checkbox("Use split-panel map")
    add_legend = st.checkbox("Add legend", True)

    if dataset == "JRC Max Water Extent (1984-2020)":
        params = params_input.text_area(
            "Enter vis params as a dictionary",
            "{'min': 1, 'max': 1, 'palette': ['0000ff']}",
        )

        try:
            vis_params = eval(params)
        except Exception as e:
            st.error(e)
            st.error("Invalid vis params")
            vis_params = {}

        image = (
            ee.Image("JRC/GSW1_3/GlobalSurfaceWater").select("max_extent").selfMask()
        )

        if st.session_state["ROI"] is not None:
            image = image.clip(st.session_state["ROI"])

        if split:
            layer = geemap.ee_tile_layer(image, vis_params, dataset, True, opacity)
            Map.split_map(layer, layer)
        else:
            Map.add_layer(image, vis_params, dataset, True, opacity)

        if add_legend:
            legend_dict = {"Water": vis_params["palette"][0]}
            Map.add_legend(title="JRC Water", legend_dict=legend_dict)

    elif dataset == "JRC Water Occurrence (1984-2020)":
        params = params_input.text_area(
            "Enter vis params as a dictionary",
            "{'min': 0, 'max': 100, 'palette': ['ffffff', 'ffbbbb', '0000ff']}",
        )

        try:
            vis_params = eval(params)
        except Exception as e:
            st.error(e)
            st.error("Invalid vis params")
            vis_params = {}

        image = ee.Image("JRC/GSW1_3/GlobalSurfaceWater").select("occurrence")

        if st.session_state["ROI"] is not None:
            image = image.clip(st.session_state["ROI"])

        if split:
            layer = geemap.ee_tile_layer(image, vis_params, dataset, True, opacity)
            Map.split_map(layer, layer)
        else:
            Map.add_layer(image, vis_params, dataset, True, opacity)

        Map.add_colorbar(vis_params, label="Water occurrence (%)")

    elif dataset == "Dynamic World 2020":
        start_date = "2020-01-01"
        end_date = "2021-01-01"

        if st.session_state["ROI"] is not None:
            region = st.session_state["ROI"]
        else:
            region = ee.Geometry.BBox(-179, -89, 179, 89)

        if water_only:
            image = geemap.dynamic_world(
                region, start_date, end_date, return_type="class"
            )

            image = image.eq(0).selfMask()

            params = params_input.text_area(
                "Enter vis params as a dictionary",
                "{'min': 1, 'max': 1, 'palette': ['419BDF']}",
            )

            try:
                vis_params = eval(params)
            except Exception as e:
                st.error(e)
                st.error("Invalid vis params")
                vis_params = {}

        else:
            image = geemap.dynamic_world(
                region, start_date, end_date, return_type="hillshade"
            )
            vis_params = {}

        if st.session_state["ROI"] is not None:
            image = image.clip(st.session_state["ROI"])

        if split:
            layer = geemap.ee_tile_layer(image, vis_params, dataset, True, opacity)
            Map.split_map(layer, layer)
        else:
            Map.add_layer(image, vis_params, dataset, True, opacity)

        if add_legend:

            if water_only:
                legend_dict = {"Water": vis_params["palette"][0]}
                Map.add_legend(title="Legend", legend_dict=legend_dict)
            else:
                Map.add_legend(
                    title="Dynamic World Land Cover", builtin_legend="Dynamic_World"
                )

    elif dataset == "ESA Global Land Cover 2020":
        image = ee.ImageCollection("ESA/WorldCover/v100").first()

        if st.session_state["ROI"] is not None:
            image = image.clip(st.session_state["ROI"])

        if water_only:
            image = image.eq(80).selfMask()

            params = params_input.text_area(
                "Enter vis params as a dictionary",
                "{'min': 1, 'max': 1, 'palette': ['0064c8']}",
            )

            try:
                vis_params = eval(params)
            except Exception as e:
                st.error(e)
                st.error("Invalid vis params")
                vis_params = {}
        else:
            vis_params = {
                "bands": ["Map"],
            }

        if split:
            layer = geemap.ee_tile_layer(image, vis_params, dataset, True, opacity)
            Map.split_map(layer, layer)
        else:
            Map.add_layer(image, vis_params, dataset, True, opacity)

        if add_legend:

            if water_only:
                legend_dict = {"Water": vis_params["palette"][0]}
                Map.add_legend(title="Legend", legend_dict=legend_dict)
            else:
                Map.add_legend(title="ESA Land Cover", builtin_legend="ESA_WorldCover")

    elif dataset == "ESRI Global Land Cover 2020":
        image = ee.ImageCollection(
            "projects/sat-io/open-datasets/landcover/ESRI_Global-LULC_10m"
        ).mosaic()

        if st.session_state["ROI"] is not None:
            image = image.clip(st.session_state["ROI"])

        if water_only:
            image = image.eq(1).selfMask()

            esri_vis = {"min": 1, "max": 1, "palette": ["#1A5BAB"]}

        else:
            esri_vis = {
                "min": 1,
                "max": 10,
                "palette": [
                    "#1A5BAB",
                    "#358221",
                    "#A7D282",
                    "#87D19E",
                    "#FFDB5C",
                    "#EECFA8",
                    "#ED022A",
                    "#EDE9E4",
                    "#F2FAFF",
                    "#C8C8C8",
                ],
            }

        params = params_input.text_area(
            "Enter vis params as a dictionary",
            str(esri_vis),
        )

        try:
            vis_params = eval(params)
        except Exception as e:
            st.error(e)
            st.error("Invalid vis params")
            vis_params = {}

        if split:
            layer = geemap.ee_tile_layer(image, vis_params, dataset, True, opacity)
            Map.split_map(layer, layer)
        else:
            Map.add_layer(image, vis_params, dataset, True, opacity)

        if add_legend:

            if water_only:
                legend_dict = {"Water": vis_params["palette"][0]}
                Map.add_legend(title="Legend", legend_dict=legend_dict)
            else:
                Map.add_legend(title="ESRI Land Cover", builtin_legend="ESRI_LandCover")
    elif dataset == "OpenStreetMap Water Layer":
        image = ee.ImageCollection(
            "projects/sat-io/open-datasets/OSM_waterLayer"
        ).mosaic()

        if st.session_state["ROI"] is not None:
            image = image.clip(st.session_state["ROI"])

        vis = {
            "min": 1,
            "max": 5,
            "palette": ["08306b", "08519c", "2171b5", "4292c6", "6baed6"],
        }

        legend_dict = {
            "Ocean": "08306b",
            "Large Lake/River": "08519c",
            "Major River": "2171b5",
            "Canal": "4292c6",
            "Small Stream": "6baed6",
        }

        params = params_input.text_area(
            "Enter vis params as a dictionary",
            str(vis),
        )

        try:
            vis_params = eval(params)
        except Exception as e:
            st.error(e)
            st.error("Invalid vis params")
            vis_params = {}

        if split:
            layer = geemap.ee_tile_layer(image, vis_params, dataset, True, opacity)
            Map.split_map(layer, layer)
        else:
            Map.add_layer(image, vis_params, dataset, True, opacity)

        if add_legend:

            Map.add_legend(title="OSM Water Layer", legend_dict=legend_dict)
    elif dataset == "Global River Width (GRWL)":
        image = ee.ImageCollection(
            "projects/sat-io/open-datasets/GRWL/water_mask_v01_01"
        ).mosaic()

        vector = ee.FeatureCollection(
            "projects/sat-io/open-datasets/GRWL/water_vector_v01_01"
        )

        if st.session_state["ROI"] is not None:
            image = image.clip(st.session_state["ROI"])
            vector = vector.filterBounds(st.session_state["ROI"])

        vis = {
            "min": 255,
            "max": 255,
            "palette": [
                "#0000ff",
            ],
        }

        params = params_input.text_area(
            "Enter vis params as a dictionary",
            str(vis),
        )

        try:
            vis_params = eval(params)
        except Exception as e:
            st.error(e)
            st.error("Invalid vis params")
            vis_params = {}

        if split:
            layer = geemap.ee_tile_layer(image, vis_params, dataset, True, opacity)
            Map.split_map(layer, layer)
        else:
            Map.add_layer(image, vis_params, dataset, True, opacity)

        Map.addLayer(
            vector.style(**{"fillColor": "00000000", "color": "FF5500"}),
            {},
            "GRWL Vector",
        )

        if add_legend:

            legend_dict = {
                "Water": vis_params["palette"][0],
                "River Centerline": "#FF5500",
            }
            Map.add_legend(title="Global River Width", legend_dict=legend_dict)

    elif dataset == "Global floodplains (GFPLAIN250m)":
        image = ee.ImageCollection("projects/sat-io/open-datasets/GFPLAIN250").mosaic()

        if st.session_state["ROI"] is not None:
            image = image.clip(st.session_state["ROI"])

        vis = {
            "palette": [
                "#0000ff",
            ],
        }

        params = params_input.text_area(
            "Enter vis params as a dictionary",
            str(vis),
        )

        try:
            vis_params = eval(params)
        except Exception as e:
            st.error(e)
            st.error("Invalid vis params")
            vis_params = {}

        if split:
            layer = geemap.ee_tile_layer(image, vis_params, dataset, True, opacity)
            Map.split_map(layer, layer)
        else:
            Map.add_layer(image, vis_params, dataset, True, opacity)

        if add_legend:

            legend_dict = {
                "Water": vis_params["palette"][0],
            }
            Map.add_legend(title="Global floodplains", legend_dict=legend_dict)

    elif dataset == "HydroLAKES":
        vector = ee.FeatureCollection(
            "projects/sat-io/open-datasets/HydroLakes/lake_poly_v10"
        )

        if st.session_state["ROI"] is not None:
            vector = vector.filterBounds(st.session_state["ROI"])

        vis = {
            "color": "#00008B",
        }

        params = params_input.text_area(
            "Enter vis params as a dictionary",
            str(vis),
        )

        try:
            vis_params = eval(params)
        except Exception as e:
            st.error(e)
            st.error("Invalid vis params")
            vis_params = {}

        if split:
            layer = geemap.ee_tile_layer(vector, vis_params, dataset, True, opacity)
            Map.split_map(layer, layer)
        else:
            Map.add_layer(vector, vis_params, dataset, True, opacity)

        if add_legend:

            legend_dict = {
                "Lake": vis_params["color"],
            }
            Map.add_legend(title="HydroLAKES", legend_dict=legend_dict)


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

    if select:
        Map.centerObject(st.session_state["ROI"])
    else:
        Map.set_center(longitude, latitude, zoom)
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
