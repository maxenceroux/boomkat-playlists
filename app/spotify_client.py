from typing import List
import requests
from retrying import retry
import base64
import json


class SpotifyController:
    def __init__(self, client_id: str, client_secret: str) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self._base_url = "https://api.spotify.com"
        self.user_id = None
        self.token = None

    @retry(stop_max_attempt_number=7, wait_fixed=2500)
    def _get_token(self):
        to_encode = f"{self.client_id}:{self.client_secret}"
        to_encode = to_encode.encode("ascii")
        base64Bytes = base64.b64encode(to_encode)
        base64Message = base64Bytes.decode("ascii")
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {base64Message}",
        }
        data = {"grant_type": "client_credentials"}
        url = "https://accounts.spotify.com/api/token"
        try:
            response = requests.post(url, headers=headers, data=data)
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            raise SystemExit(err)
        return response.json()["access_token"]

    @retry(stop_max_attempt_number=7, wait_fixed=2500)
    def get_current_user_id(self, token: str):
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }
        url = f"{self._base_url}/v1/me"
        try:
            response = requests.get(url, headers=headers)
            print(response.text)
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            raise SystemExit(err)
        return response.json()["id"]

    @retry(stop_max_attempt_number=7, wait_fixed=2500)
    def create_playlist(
        self,
        token: str,
        playlist_name: str,
        description: str = None,
        public: bool = None,
    ):
        if not self.user_id:
            self.user_id = self.get_current_user_id(token)
            print("here")
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }
        url = f"{self._base_url}/v1/users/{self.user_id}/playlists"
        payload = {
            "name": playlist_name,
            "description": description,
            "public": public,
        }
        try:
            response = requests.post(
                url, headers=headers, data=json.dumps(payload)
            )
            print(response.text)
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            raise SystemExit(err)
        return response.json()

    @retry(stop_max_attempt_number=7, wait_fixed=2500)
    def get_playlist_tracks(self, token: str, playlist_id: str):
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }
        url = f"{self._base_url}/v1/playlists/{playlist_id}/tracks"
        tracks = []
        while url:
            try:
                response = requests.get(url, headers=headers)
                response.raise_for_status()
            except requests.exceptions.HTTPError as err:
                raise SystemExit(err)
            for item in response.json()["items"]:
                if "id" in item["track"]:

                    tracks.append(
                        {
                            "track_id": item["track"]["id"],
                            "uri": item["track"]["uri"],
                            "album_image_url": item["track"]["album"]["images"][
                                0
                            ]["url"],
                        }
                    )
            url = response.json()["next"]
        return tracks

    @retry(stop_max_attempt_number=7, wait_fixed=2500)
    def delete_all_playlist_items(
        self,
        token: str,
        playlist_id: str,
    ):
        playlist_tracks = self.get_playlist_tracks(token, playlist_id)
        uris = [
            {"uri": track["uri"]} for _, track in enumerate(playlist_tracks)
        ]
        for i in range(0, len(uris), 100):
            tmp_track_uris = uris[i : i + 100]
            data = {"tracks": tmp_track_uris}
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}",
            }
            url = f"{self._base_url}/v1/playlists/{playlist_id}/tracks"

            try:
                response = requests.delete(url, headers=headers, json=data)
                response.raise_for_status()
            except requests.exceptions.HTTPError as err:
                raise SystemExit(err)
        return True

    @retry(stop_max_attempt_number=7, wait_fixed=2500)
    def search(self, q: str, type: str):
        if not self.token:
            self.token = self._get_token()
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}",
        }
        url = f"{self._base_url}/v1/search"
        params = {
            "q": q,
            "type": type,
        }
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            if response.json().get("error"):
                return {"message": "ID corresponding to no playlist"}
        results = {}
        res = []
        if response.json().get(f"{type}s"):
            for item in response.json().get(f"{type}s")["items"]:
                res.append(
                    {
                        "artist_id": item.get("artists")[0]["id"],
                        "artist_name": item.get("artists")[0]["name"],
                        "album_id": item.get("id"),
                        "album_name": item.get("name"),
                        "image_url": item.get("images")[0]["url"],
                    }
                )
        results["items"] = res
        return results

    @retry(stop_max_attempt_number=7, wait_fixed=2500)
    def get_album_tracks(self, album_spotify_id):
        if not self.token:
            self.token = self._get_token()
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}",
        }
        url = f"{self._base_url}/v1/albums/{album_spotify_id}/tracks"
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            if response.json().get("error"):
                return {"message": "ID corresponding to no playlist"}
        results = {}
        tracks = []
        if response.json().get("items"):
            for item in response.json().get("items"):
                tracks.append(
                    {
                        "track_name": item.get("name"),
                        "track_id": item.get("id"),
                        "uri": item.get("uri"),
                    }
                )
        results["tracks"] = tracks
        return results

    @retry(stop_max_attempt_number=7, wait_fixed=2500)
    def add_tracks_to_playlist(
        self,
        token: str,
        track_uris,
        playlist_id: str,
    ):
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }
        url = f"{self._base_url}/v1/playlists/{playlist_id}/tracks"

        data = {"uris": track_uris}
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            raise SystemExit(err)
        return True

    @retry(stop_max_attempt_number=7, wait_fixed=2500)
    def add_albums_tracks_to_playlist(self, token, albums_ids, playlist_id):
        track_uris = []
        for album_id in albums_ids:
            tracks = self.get_album_tracks(album_id)["tracks"]
            track_uris += [track["uri"] for track in tracks]
        for i in range(0, len(track_uris), 100):
            tmp_track_uris = track_uris[i : i + 100]
            self.add_tracks_to_playlist(
                token, track_uris=tmp_track_uris, playlist_id=playlist_id
            )
        return True

    @retry(stop_max_attempt_number=7, wait_fixed=2500)
    def modify_playlist_image(
        self, token: str, playlist_id: str, image_path: str
    ):
        headers = {
            "Content-Type": "image/jpeg",
            "Authorization": f"Bearer {token}",
        }
        url = f"{self._base_url}/v1/playlists/{playlist_id}/images"
        with open(image_path, "rb") as f:
            image_data = f.read()
            encoded_string = base64.b64encode(image_data)
        response = requests.put(url, headers=headers, data=encoded_string)
        return True
