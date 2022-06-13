import streamlit as st
import leafmap.foliumap as leafmap

st.set_page_config(layout="wide")

# Customize the sidebar
markdown = """
Web App URL: <https://water.streamlitapp.com>

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


st.title("Interactive Map")

col1, col2 = st.columns([4, 1])
options = list(leafmap.basemaps.keys())
index = options.index("OpenTopoMap")

with col2:

    basemap = st.selectbox("Select a basemap:", options, index)


with col1:

    m = leafmap.Map(locate_control=True, latlon_control=True, draw_export=True, minimap_control=True)
    m.add_basemap(basemap)
    m.to_streamlit(height=700)
