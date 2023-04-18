from spotify_client import SpotifyController
from boomkat_scrapper import BoomkatScrapper
from playlist_cover_creator import CoverGenerator
from spotify_scrapper import SpotifyScrapper
import os
import pandas as pd
import json
import logging


def add_bestsellers_to_playlist(playlist_id, bestsellers):
    scrapper = SpotifyScrapper(
        chromedriver="prod",
        spotify_user=os.environ["SPOTIFY_USER"],
        spotify_password=os.environ["SPOTIFY_PASSWORD"],
    )
    token = scrapper.get_spotify_token()
    client = SpotifyController(
        os.environ["SPOTIFY_CLIENT_ID"], os.environ["SPOTIFY_CLIENT_SECRET"]
    )
    client.delete_all_playlist_items(token, playlist_id)
    album_ids = list(bestsellers["album_id"].unique())
    client.add_albums_tracks_to_playlist(token, album_ids, playlist_id)
    return token


def update_playlists():
    with open(os.environ["GENRE_DICT_PATH"]) as f:
        genre_dict = json.load(f)
    for g in genre_dict:
        bestsellers = get_bestsellers(g["genre_id"])
        print(g["genre"], bestsellers.shape)
        playlist_id = g["playlist_id"]
        token = add_bestsellers_to_playlist(playlist_id, bestsellers)
        base_image_path = f"static/boomkat_{g['genre']}.png"
        update_playlist_cover(token, playlist_id, bestsellers, base_image_path)


def update_playlist_cover(token, playlist_id, bestsellers, base_image_path):
    image_urls = list(bestsellers["image_url"].unique())
    cover_gen = CoverGenerator()
    image = cover_gen.create_playlist_cover(image_urls, base_image_path)
    image.save("ordered_images.jpeg")
    client = SpotifyController(
        os.environ["SPOTIFY_CLIENT_ID"], os.environ["SPOTIFY_CLIENT_SECRET"]
    )
    client.modify_playlist_image(token, playlist_id, "ordered_images.jpeg")
    os.remove("ordered_images.jpeg")


def get_bestsellers(genre_id=None):
    boomkat = BoomkatScrapper("prod")
    if genre_id == "recommended":
        albums_list = boomkat.get_recommended_list()
    elif genre_id == "bestsellers":
        albums_list = boomkat.get_bestsellers_list(None)
    else:
        albums_list = boomkat.get_bestsellers_list(genre_id)
    bestsellers = pd.DataFrame(albums_list)
    bestsellers = bestsellers.reset_index().rename(columns={"index": "rank"})
    bestsellers = get_boomkat_album_spotify_id(bestsellers)
    bestsellers = bestsellers.dropna()
    boomkat.quit()
    return bestsellers


def get_boomkat_album_spotify_id(bestsellers_df):
    client = SpotifyController(
        os.environ["SPOTIFY_CLIENT_ID"], os.environ["SPOTIFY_CLIENT_SECRET"]
    )

    for idx, row in bestsellers_df.iterrows():
        search_artist_name, search_album_name = (
            row["artist"]
            .lower()
            .split("(")[0]
            .split(" & ")[0]
            .split(" x ")[0]
            .strip(),
            row["album"].lower().split("(")[0].strip(),
        )
        query = f"{search_artist_name} {search_album_name}"
        try:
            search_result = pd.DataFrame(
                client.search(q=query, type="album")["items"]
            )
            search_result.loc[:, "artist_name"] = (
                search_result["artist_name"]
                .str.lower()
                .str.split("(")
                .str[0]
                .str.strip()
            )
            search_result.loc[:, "album_name"] = (
                search_result["album_name"]
                .str.lower()
                .str.split("(")
                .str[0]
                .str.strip()
            )
            filtered = search_result[
                (search_result["album_name"].str.contains(search_album_name))
                & (
                    search_result["artist_name"].str.contains(
                        search_artist_name
                    )
                )
            ]
            if filtered.shape[0] > 0:
                bestsellers_df.loc[idx, "album_id"] = filtered.iloc[0][
                    "album_id"
                ]
                bestsellers_df.loc[idx, "image_url"] = filtered.iloc[0][
                    "image_url"
                ]
        except:
            pass
    return bestsellers_df
