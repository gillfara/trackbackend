from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime
from database import create_db_and_tables
from pydantic import EmailStr


class UserBase(SQLModel):
    username: str = Field(index=True)
    email: EmailStr
    password: str


class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class TrackBase(SQLModel):
    name: str


class Track(TrackBase, table=True):
    id: int = Field(default=None, primary_key=True)
    path: str

class TrackPub(SQLModel):
    name:str
    path:str


# class ArtistBase(SQLModel):
#     name: str


# class Artist(ArtistBase, table=True):
#     id: int | None = Field(default=None, primary_key=True)
#     tracks: list["Artist"] = Relationship(back_populates="artist")


# class TrackBase(SQLModel):
#     title: str
#     path: str


# class TrackPlaylist(SQLModel, table=True):
#     playlist_id: int | None = Field(
#         default=None, foreign_key="playlist.id", primary_key=True)
#     track_id: int | None = Field(default=None, foreign_key="track.id", primary_key=True)


# class Track(TrackBase, table=True):
#     id: int | None = Field(default=None, primary_key=True)
#     artist_id: int | None = Field(foreign_key="artist.id")
#     artist: Artist = Relationship(back_populates="tracks")
#     playlists: list["PlayList"] = Relationship(
#         back_populates="tracks", link_model=TrackPlaylist
#     )


# class PlayListBase(SQLModel):
#     name: str


# class PlayList(PlayListBase,table=True):
#     id: int | None = Field(default=None, primary_key=True)
#     user_id: int = Field(foreign_key="user.id")
#     user: User = Relationship(back_populates="playlist")
#     tracks: list["Track"] = Relationship(
#         back_populates="playlists", link_model=TrackPlaylist
#     )
