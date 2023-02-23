from utils import get_earthquake_data, add_distance_column, filter_data, add_my_location
import streamlit as st
import geocoder

database = get_earthquake_data()

lat, lon = None, None

st.title("Deprem Filtreleme Uygulaması")

min_mag = st.slider(label="Minimum Büyüklük", min_value=0.0, max_value=10.0, value=3.0, step=0.1)
max_dist = st.slider(label="Maksimum Uzaklık", min_value=0, max_value=1670, value=200, step=10)

loc_button = st.button(label="Konumu Al")
if loc_button:
    res = g = geocoder.ip('me')


    st.session_state['lat'] = res.latlng[0]
    st.session_state['lon'] = res.latlng[1]

    st.text(f"Enlem: {res.latlng[0]}")
    st.text(f"Boylam: {res.latlng[1]}")

submit = st.button(label="Submit")
if submit:
    if 'lat' not in st.session_state or 'lon' not in st.session_state:
        st.error("Lütfen önce konumunuzu belirleyin!")
        st.stop()
    st.text(f"Enlem: {st.session_state['lat']}")
    st.text(f"Boylam: {st.session_state['lon']}")

    data = database.copy()
    data = add_distance_column(data, st.session_state['lat'], st.session_state['lon'])
    data = filter_data(data, min_mag, max_dist)

    st.table(data)

    data = add_my_location(data, st.session_state['lat'], st.session_state['lon'])

    st.map(data)