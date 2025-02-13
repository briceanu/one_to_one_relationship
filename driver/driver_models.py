from pydantic import BaseModel, Field, EmailStr, field_validator,model_validator
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from sqlalchemy import String, ForeignKey
import uuid
from datetime import date
from db.db_connection import Base 


"""driver model"""

class Driver(Base):
    __tablename__ = 'driver'

    driver_id: Mapped[uuid.UUID] = mapped_column(default=lambda:uuid.uuid4(),primary_key=True)
    name:Mapped[str] = mapped_column(String(40))
    email:Mapped[str] = mapped_column(String(80),unique=True)
    date_of_birth:Mapped[date] = mapped_column(nullable=False)
    address :Mapped[str] = mapped_column(String(120))
    truck_id:Mapped[uuid.UUID] = mapped_column(ForeignKey('truck.truck_id'), unique=True)
    truck:Mapped["Truck"] = relationship("Truck",back_populates='driver', cascade='all, delete')


    def __repr__(self):
        return f"<Driver(name={self.name}, email={self.email}, truck_id={self.truck_id})>"

    @validates('date_of_birth')
    def validate_date(self,key,value):
        lowest_date= date(1950,1,1)
        if value < lowest_date:
            raise ValueError('date of birth can not be less than 01-01-1950')
        return value


#######################################################################################
"""pydantic model"""

class Driver_pydantic_model(BaseModel):
    name:str= Field(max_length=40)
    email:EmailStr = Field()
    date_of_birth:date = Field()
    address:str = Field(max_length=100)
    truck_id:uuid.UUID = Field()
 
 

    class Config:
        from_attributes = True
        extra = 'forbid'

    @field_validator('name')
    @classmethod
    def check_name_not_empty(cls, value):
        if not value or value == "":
            raise ValueError('Name cannot be empty')
        return value
    
    @field_validator('date_of_birth')
    @classmethod
    def validate_date(cls,value):
        lowest_date= date(1950,1,1)
        if value < lowest_date:
            raise ValueError('date of birth can not be less than 01-01-1950')
        return value
    





class Driver_update_pydantic_model(BaseModel):
    name:str= Field(max_length=40)

    @field_validator('name')
    @classmethod
    def check_name_not_empty(cls, value):
        if not value or value == "":
            raise ValueError('Name cannot be empty')
        return value
    









from truck.truck_models import Truck