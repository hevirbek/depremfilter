from utils import get_earthquake_data, add_distance_column, filter_data, add_my_location, HiddenPrints
import streamlit as st
import streamlit.components.v1 as components
from streamlit_ws_localstorage import injectWebsocketCode, getOrCreateUID

# Main call to the api, returns a communication object
with HiddenPrints():
    conn = injectWebsocketCode(hostPort='linode.liquidco.in', uid=getOrCreateUID())

database = get_earthquake_data()

st.title("Deprem Filtreleme Uygulaması")

min_mag = st.slider(label="Minimum Büyüklük", min_value=0.0, max_value=10.0, value=3.0, step=0.1)
max_dist = st.slider(label="Maksimum Uzaklık", min_value=0, max_value=1670, value=200, step=10)

template = """
<script type="text/javascript">
    var lat, lon;
    navigator.geolocation.getCurrentPosition(function(position) {
        lat = position.coords.latitude;
        lon = position.coords.longitude;

        localStorage.setItem("coords", lat+","+lon);
    });
</script>
"""

remove_newlines = lambda s: s.replace("\n", "").replace("\r", "").strip().replace(" ", "").replace("\t", "")

html = components.html(template, height=0, width=0)

submit = st.button(label="Filtrele")
if submit:
    with st.spinner('İşleniyor...'):
        if 'lat' not in st.session_state or 'lon' not in st.session_state:
            with HiddenPrints():
                coords = conn.getLocalStorageVal(key='coords')

            lat, lon = coords.split(",")

            st.session_state['lat'] = float(lat)
            st.session_state['lon'] = float(lon)

    st.text(f"Enlem: {st.session_state['lat']}")
    st.text(f"Boylam: {st.session_state['lon']}")

    data = database.copy()
    data = add_distance_column(data, st.session_state['lat'], st.session_state['lon'])
    data = filter_data(data, min_mag, max_dist)

    st.table(data)

    data = add_my_location(data, st.session_state['lat'], st.session_state['lon'])

    st.map(data)
