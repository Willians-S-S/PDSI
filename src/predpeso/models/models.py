import enum 
from datetime import datetime
from sqlalchemy import ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from predpeso.db.base import Base

class UserFarmRole(str, enum.Enum):
    ADMIN = "admin"
    CUIDADOR = "cuidador"


class UserModel(Base):
    __tablename__ = 'user'

    id: Mapped[str] = mapped_column(primary_key=True, unique= True)
    name: Mapped[str] = mapped_column(nullable=False)
    username: Mapped[str] = mapped_column(nullable=False, unique=True)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    password: Mapped[str] = mapped_column(nullable=False)
    cpf: Mapped[str] = mapped_column(nullable=False, unique=True)
    profile_picture: Mapped[str] = mapped_column(nullable=True)
    role: Mapped[UserFarmRole] = mapped_column(SQLEnum(UserFarmRole, name="user_farm_role_enum", create_type=False), nullable=False)
    created_at: Mapped[datetime] = mapped_column(nullable=False)
    updated_at: Mapped[datetime] = mapped_column(nullable=False)

    def __repr__(self):
        return f"<User id={self.id} username='{self.username}'>"
