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

    farm_associations: Mapped[list["UserFarmAssociation"]] = relationship(
        "UserFarmAssociation", 
        back_populates="user", 
        cascade="all, delete-orphan", 
        passive_deletes=True 
    )

    def __repr__(self):
        return f"<User id={self.id} username='{self.username}'>"
    
class UserFarmAssociation(Base):
    __tablename__ = 'user_farm_association'

    user_id: Mapped[str] = mapped_column(ForeignKey('user.id', ondelete="CASCADE"), primary_key=True)
    farm_id: Mapped[str] = mapped_column(ForeignKey('farm.id', ondelete="CASCADE"), primary_key=True)

    user: Mapped["UserModel"] = relationship(back_populates="farm_associations")
    farm: Mapped["FarmModel"] = relationship(back_populates="user_associations")

    def _repr_(self):
        return f"<UserFarmAssociation user_id={self.user_id} farm_id={self.farm_id} role='{self.role.value}'>"
    

class FarmModel(Base):
    __tablename__ = 'farm'

    id: Mapped[str] = mapped_column(primary_key=True, unique= True)
    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=True)
    animal_quantity: Mapped[int] = mapped_column(nullable=False, default=0) 
    created_at: Mapped[datetime] = mapped_column(nullable=False)
    updated_at: Mapped[datetime] = mapped_column(nullable=False)

    user_associations: Mapped[list["UserFarmAssociation"]] = relationship(
        "UserFarmAssociation",
        back_populates="farm",  
        cascade="all, delete-orphan", 
        passive_deletes=True 
    )

    animals: Mapped[list["AnimalModel"]] = relationship("AnimalModel",
                                                        back_populates="farm",
                                                        cascade="all, delete",
                                                        passive_deletes=True
                                                        )


class AnimalModel(Base):
    __tablename__ = 'animal'

    id: Mapped[str] = mapped_column(primary_key=True, unique= True)
    name: Mapped[str] = mapped_column(nullable=False)
    breed: Mapped[str] = mapped_column(nullable=True)
    age: Mapped[int] = mapped_column(nullable=True)
    gender: Mapped[str] = mapped_column(nullable=False)
    image_url: Mapped[str] = mapped_column(nullable=True)
    health_condition: Mapped[str] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(nullable=False)
    updated_at: Mapped[datetime] = mapped_column(nullable=False)

    farm_id: Mapped[str] = mapped_column(ForeignKey("farm.id", ondelete="CASCADE"), nullable=False)
    
    farm: Mapped["FarmModel"] = relationship("FarmModel",
                                             back_populates="animals") 
    
    historys: Mapped[list["History"]] = relationship("History",
                                                     back_populates="animal",
                                                     cascade="all, delete-orphan",
                                                     passive_deletes=True
                                                     )


class History(Base):
    __tablename__ = 'history'

    id: Mapped[str] = mapped_column(primary_key=True, unique= True)
    weight_manual: Mapped[float] = mapped_column(nullable=True)
    current_weight: Mapped[float] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(nullable=False)

    animal_id: Mapped[str] = mapped_column(ForeignKey("animal.id", ondelete="CASCADE"), nullable=False)
    animal: Mapped["AnimalModel"] = relationship("AnimalModel",
                                                 back_populates="historys")
