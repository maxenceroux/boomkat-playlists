# Boomkat Bestsellers Scraper and Spotify Playlist Creator

This is a Python project that scrapes the Boomkat bestsellers page using Selenium and creates daily Spotify playlists based on the top tracks.
Scripting is exposed through an API server using FastAPI. FastAPI server and Selenium driver are containerized in Docker containers.

## Requirements

- Python 3.7+
- Docker Compose
- Spotify Developer Account

## Installation

1. Clone the repository to your local machine.
2. Build Docker Images using the following make command: `make build-docker`
3. Run your containers using the following make command: `make start-docker`
4. Stop your containers using the following make command: `make stop-docker`

You can run your Docker containers on ARM architectures (Raspberry Pi) using the same commands suffixed with `-arm`. e.g. `make start-docker-arm`

## Configuration

1. Create a Spotify Developer Account and create a new application here.
2. Set the SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET environment variables to the values provided by your Spotify application.
3. Set the SPOTIPY_REDIRECT_URI environment variable to a valid redirect URI for your Spotify application (e.g. http://localhost:8888/callback).
4. `.env` should contain the following:

```sh
SPOTIFY_CLIENT_ID=
SPOTIFY_CLIENT_SECRET=
SPOTIFY_USER=
SPOTIFY_PASSWORD=
GENRE_DICT_PATH="static/genre_dict.json"
```

## Usage

To run the scraper and create playlists:

1. Once API server is available: head to http://localhost:8001
2. Call the POST endpoint: `/boomkat_playlist`

The scraper will launch a Chrome browser window and navigate to the Boomkat bestsellers page.
The script will then scrape the top tracks and create a new Spotify playlist with those tracks for each genres.

## Credits

This project was created by Maxence Roux as a personal project.

## License

This project is licensed under the MIT License. See the LICENSE file for more information.
