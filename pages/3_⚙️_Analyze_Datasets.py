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

st.title("Split-panel Map")

with st.expander("See source code"):
    with st.echo():
        m = leafmap.Map()
        m.split_map(
            left_layer="ESA WorldCover 2020 S2 FCC", right_layer="ESA WorldCover 2020"
        )
        m.add_legend(title="ESA Land Cover", builtin_legend="ESA_WorldCover")

m.to_streamlit(height=700)
