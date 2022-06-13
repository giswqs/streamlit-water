import streamlit as st
import leafmap.foliumap as leafmap

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

# Customize page title
st.title("Global Surface Water Explorer")

st.markdown(
    """
    This interactive web app demonstrates how to visualize and compare global surface water datasets. Click the on side bar menu to explore the different datasets.
    """
)

# st.markdown(markdown)

m = leafmap.Map(minimap_control=False)
m.add_basemap("HYBRID")
m.add_basemap("ESA WorldCover 2020 S2 FCC")
m.add_basemap("ESA WorldCover 2020 S2 TCC")
m.add_basemap("ESA WorldCover 2020")
m.add_legend(title="ESA Land Cover", builtin_legend="ESA_WorldCover")
m.to_streamlit(height=700)
