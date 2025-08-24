import streamlit as st
from SpotifyWrapper import SpotifyWrapper
from PosterGenerator import PosterGenerator
from PosterType import PosterType
import random
import io



@st.cache_resource
def get_spotify_wrapper():
    return SpotifyWrapper()

@st.cache_resource
def read_album_list():
    try:
        with open("apple100.txt", "r", encoding="utf-8") as file:
            lines = file.readlines()
            return [line.strip() for line in lines]
    except FileNotFoundError:
        print(f"Error: File apple100.txt not found.")
        return []
    except Exception as e:
        print(f"Error reading file: {e}")
        return []

def render(pstyle="Auto"):
    search_res=sw.search_album(st.session_state['search_string'],1)
    st.session_state.album=search_res['albums']['items'][0]

    album_data, tracks_data=sw.get_album_details(st.session_state.album['id'])
    st.session_state.tracks=tracks_data
    poster_type=  PosterType()
    poster_type.poster_8x10()
    poster = pg.generate_poster(sw,poster_type,st.session_state.album,st.session_state.tracks,pstyle)
    st.image(poster)

    buf = io.BytesIO()
    poster.save(buf, format="PNG", dpi=(300, 300))
    buf.seek(0)
    album_name=st.session_state.album['name']
    artist_name = ", ".join([artist['name'] for artist in st.session_state.album['artists']])

    
    st.download_button(
        label="📥 Download High-Quality Poster (300 DPI)",
        data=buf,
        file_name=f"{artist_name.replace(' ', '_')}_{album_name.replace(' ', '_')}_poster.png",
        mime="image/png",
        type="secondary")
    

sw = get_spotify_wrapper()
#album_db=sw.search_popular_albums()
album_db=read_album_list()
random_album=album_db[random.randint(1, len(album_db))]

if 'search_string' in st.session_state:
    st.session_state.search_string=st.session_state.search_string
else:
    st.session_state.search_string=random_album

pg = PosterGenerator()

st.session_state['search_string'] = st.text_input("Search artist + record name",value=st.session_state['search_string'])

if 'album_data' in st.session_state:
    st.session_state.album_data=st.session_state.album_data
else:
    st.session_state.album_data=None

col1, col2,col3 = st.columns([1,1,1])
with col1:
    poster_style=st.selectbox("Poster style",("Auto","Standard","Long name"))
with col2:
    srch_btn=st.button("Search",type="primary")
with col3:
    random_btn=st.button("Random",type="primary")

if srch_btn and st.session_state['search_string']:
    render(poster_style)
elif st.session_state['search_string']:
    render(poster_style)

if random_btn:
    #st.session_state.album_data=None
    random_album=album_db[random.randint(1, len(album_db))]
    st.session_state.search_string=random_album
    st.rerun()
