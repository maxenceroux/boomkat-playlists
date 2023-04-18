from fastapi import FastAPI, BackgroundTasks
from utils import *


app = FastAPI()


@app.post("/boomkat_playlist")
async def update_boomkat_playlist(background_tasks: BackgroundTasks):
    background_tasks.add_task(update_playlists)
    return {"message": "playlist updates started"}
