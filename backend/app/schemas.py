from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Status = Literal["running", "stopped", "exited"]


# ---------- Whales ----------
class WhaleBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=80)
    emoji: str = Field(default="🐳", max_length=8)


class WhaleCreate(WhaleBase):
    pass


class WhaleOut(WhaleBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


# ---------- Containers ----------
class ContainerBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    image: str = Field(default="nginx:latest", max_length=200)
    status: Status = "running"
    whale_id: int


class ContainerCreate(ContainerBase):
    pass


class ContainerUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    image: str | None = Field(default=None, max_length=200)
    status: Status | None = None
    whale_id: int | None = None


class ContainerOut(ContainerBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
