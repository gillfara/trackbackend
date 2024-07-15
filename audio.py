from fastapi import FastAPI, HTTPException , Header,Depends,status,BackgroundTasks,UploadFile,Path
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.requests import Request
import tempfile
from fastapi.middleware.cors import CORSMiddleware
import os
from typing import Annotated
from pydantic import BaseModel
from models import UserBase,User,TrackBase,Track,TrackPub
from sqlmodel import Session,select
from security import get_current_user,authenticate_user,create_token,Token,get_password_hash
from database import create_db_and_tables,engine
from file import convert_mp3_to_hls
from io import BytesIO


class UserModel(BaseModel):
    username:str
    password:str


def get_session():
    with Session(engine) as session:
        yield session


app = FastAPI()


create_db_and_tables()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


# Define the directory for HLS outputs
HLS_DIR = "hls_output"

# Mount the directory to serve static files
app.mount("/hls", StaticFiles(directory=HLS_DIR), name="hls")
@app.get("/audio", response_class=HTMLResponse)
async def get_page():
    message = """
    <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Audio Player</title>
    <link rel="stylesheet" href="styles.css">
    <script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script>
</head>
<body>
    <h1>Audio Player</h1>
    <audio id="audioPlayer" controls></audio>
    <script>
        var audio = document.getElementById('audioPlayer');
        var hls = new Hls();
        hls.loadSource('/hls/alone.m3u8');
        hls.attachMedia(audio);
        hls.on(Hls.Events.MANIFEST_PARSED, function() {
            audio.play();
        });
    </script>
</body>
</html>

    """
    return HTMLResponse(content=message)


def get_header(token:str|None = Header(None)):
    return token

@app.get("/hls/{filename}")
def serve_hls(filename: str):
    file_path = os.path.join(HLS_DIR, filename)
    print(file_path)
    if os.path.exists(file_path):
        if filename.endswith(".m3u8"):
            return FileResponse(file_path, media_type="application/vnd.apple.mpegurl")
        elif filename.endswith(".ts"):
            return FileResponse(file_path, media_type="video/MP2T")
    raise HTTPException(status_code=404, detail="File not found")

@app.get("/head")
async def get_head(head:Annotated[str|None,Depends(get_header)]):
    print(head)
    return "succesful"

@app.get("/users",response_model=list[UserBase])
async def get_users(session:Session=Depends(get_session)):
    users = session.exec(select(User)).all()
    return users

@app.get("/music", response_model=list[TrackPub])
async def get_music_list(session: Annotated[Session, Depends(get_session)]):
    tracks = session.exec(select(Track)).all()
    return tracks


@app.get("/{user_id}")
async def get_user(user_id:Annotated[int,Path(title="user id")],user:str=Depends(get_current_user)):
    print(user)
    return user_id


@app.post("/login")
async def login(user:UserModel):
    user = authenticate_user(**user.model_dump())
    # print(user)
    if not user:
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="incorect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )
    access_token = create_token(data={"sub":user.username})
    # print(access_token)
    return Token(token=access_token,type="bearer")



@app.post("/music")
async def save_track(track:UploadFile,backgroud:BackgroundTasks,session:Annotated[Session,Depends(get_session)]):
    tracki = await track.read()
    trackb = BytesIO(tracki)
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(trackb.getvalue())
        tempfile_path = temp_file.name
    name = f"{track.filename.split(".mp")[0]}"
    dbtrack = Track(name=track.filename,path=f"{name}.m3u8")
    backgroud.add_task(convert_mp3_to_hls,tempfile_path,output_directory="hls_output",name=name)
    session.add(dbtrack)
    session.commit()
    return "ok"



@app.post("/register",response_model=UserBase)
async def register_user(user:UserBase,session:Session=Depends(get_session)):
    user = User.model_validate(user)
    user.password = get_password_hash(user.password)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user



if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)
