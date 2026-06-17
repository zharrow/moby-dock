from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Whale(Base):
    """Une baleine = un "capitaine" qui transporte des conteneurs. 🐳"""

    __tablename__ = "whales"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    emoji: Mapped[str] = mapped_column(String(8), default="🐳")

    containers: Mapped[list["Container"]] = relationship(
        back_populates="whale",
        cascade="all, delete-orphan",
    )


class Container(Base):
    """Un conteneur transporté par une baleine."""

    __tablename__ = "containers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    image: Mapped[str] = mapped_column(String(200), default="nginx:latest")
    status: Mapped[str] = mapped_column(String(20), default="running")  # running | stopped | exited
    whale_id: Mapped[int] = mapped_column(ForeignKey("whales.id"))

    whale: Mapped["Whale"] = relationship(back_populates="containers")
