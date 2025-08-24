import streamlit as st
import requests
import base64
from PIL import Image
import io
from datetime import datetime, timedelta

class SpotifyWrapper:

    def __init__(self):
        self.token = None
        self.token_expires_at=None
    
    def __manageToken(self):
        if not self.token or not self.token_expires_at or datetime.now() >= self.token_expires_at:
            auth_header = base64.b64encode(f"{st.secrets['SPOTIFY_CLIENT_ID']}:{st.secrets['SPOTIFY_CLIENT_SECRET']}".encode()).decode()
            headers = {
                'Authorization': f'Basic {auth_header}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            data = {
                'grant_type': 'client_credentials'
            }
            try:
                response = requests.post("https://accounts.spotify.com/api/token", headers=headers, data=data)
                response.raise_for_status()
                self.token=response.json().get('access_token')
                self.token_expires_at=datetime.now() + timedelta(seconds=response.json().get('expires_in') - 300)
            except Exception as e:
                st.error(f"Failed to connect to Spotify: {str(e)}")


    def search_album(self,album_name,limit):
        self.__manageToken()
        headers = {
        'Authorization': f'Bearer {self.token}'
        }
        params = {
            'q': album_name,
            'type': 'album',
            'limit': limit
        }

        try:
            response = requests.get("https://api.spotify.com/v1/search", headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"Failed to search Spotify: {str(e)}")
        return None
    
    def get_album_details(self,album_id):
        self.__manageToken()
        if not self.token:
            return None,None
    
        album_url = f"https://api.spotify.com/v1/albums/{album_id}"
        tracks_url = f"https://api.spotify.com/v1/albums/{album_id}/tracks"
    
        headers = {
            'Authorization': f'Bearer {self.token}'
        }

        try:
            # Get album info
            album_response = requests.get(album_url, headers=headers)
            album_response.raise_for_status()
            album_data = album_response.json()
            
            # Get tracks
            tracks_response = requests.get(tracks_url, headers=headers, params={'limit': 50})
            tracks_response.raise_for_status()
            tracks_data = tracks_response.json()
            
            return album_data, tracks_data
        except Exception as e:
            st.error(f"Failed to get album details: {str(e)}")
            return None, None


    def get_album_cover_from_url(self,url):
        self.__manageToken()
        try:
            response = requests.get(url)
            album_cover = Image.open(io.BytesIO(response.content))
            return album_cover
        except Exception as e:
                st.error(f"Failed to load album cover: {str(e)}")

    def get_scan_code(self,id):
        self.__manageToken()
        try:
            url=f"https://scannables.scdn.co/uri/plain/png/FFFFFF/black/640/spotify:album:{id}"
            response = requests.get(url)
            scan_code = Image.open(io.BytesIO(response.content))
            return scan_code
        except Exception as e:
            st.error(f"Failed to load scan code: {str(e)}")

    def search_popular_albums(self, genres=None, limit: int = 100):
        if genres is None:
            genres = ["pop", "hip-hop", "rock", "electronic", "indie", "r&b"]
        
        all_albums = []
        album_ids = set()
        
        self.__manageToken()
        headers = {
        'Authorization': f'Bearer {self.token}'
        }
        
        for genre in genres:
            url = "https://api.spotify.com/v1/search"
            params = {
                "q": f"genre:{genre}",
                "type": "album",
                "limit": min(limit // len(genres), 50),
                "market": "US"
            }
            
            try:
                response = requests.get(url, headers=headers, params=params)
                response.raise_for_status()
                
                data = response.json()
                albums = data.get("albums", {}).get("items", [])
                
                for album in albums:
                    album_id = album["name"]
                    print(album_id)
                    if album_id not in album_ids:
                        album_ids.add(album_id)
                        all_albums.append(album)
                        
                        if len(all_albums) >= limit:
                            break
                
                if len(all_albums) >= limit:
                    break
                    
            except requests.RequestException as e:
                print(f"Error searching albums for genre {genre}: {e}")
                continue
        
        return all_albums