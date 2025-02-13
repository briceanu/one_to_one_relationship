from sqlalchemy.orm import Mapped,mapped_column ,relationship
from sqlalchemy import Enum, Float, Numeric,String
from db.db_connection import Base
import uuid
import enum
from pydantic import BaseModel ,Field, field_validator, PositiveFloat
from typing import Type


class FuelType(enum.Enum):
    DIESEL = "Diesel"
    LPG = "LPG"


class TruckBrand(enum.Enum):
    SCANIA = "Scania"
    MERCEDES = "Mercedes"
    VOLVO = 'Volvo'




class Truck(Base):
    __tablename__ = 'truck'
    fuel_type :Mapped[FuelType]= mapped_column(Enum(FuelType, native_enum=False))
    truck_brand:Mapped[TruckBrand]=mapped_column(Enum(TruckBrand, native_enum=False))
    truck_id:Mapped[uuid.UUID]= mapped_column(default=lambda:uuid.uuid4(), primary_key=True) 
    number_plate:Mapped[str]= mapped_column(String(60),unique=True)
    distance_driven :Mapped[Float] = mapped_column(Numeric(7,2),  nullable=False)
    driver:Mapped["Driver"] = relationship("Driver",back_populates='truck', uselist=False)

    def __reper__(self):
        return f'Brand {self.truck_brand}, number plate {self.number_plate}'


############################################################################

"""pydantic model"""


class Truck_pydantic_model(BaseModel):
    number_plate:str = Field(max_length=60)
    truck_brand: TruckBrand
    fuel_type: FuelType
    distance_driven: PositiveFloat
    # distance_driven: float = Field(ge=0.0)

    @field_validator("fuel_type")
    @classmethod
    def check_fuel_type(cls, value: str) -> str:
        return cls.validate_enum(value, FuelType, "fuel_type")

    @field_validator("truck_brand")
    @classmethod
    def check_truck_brand(cls, value: str) -> str:
        return cls.validate_enum(value, TruckBrand, "truck_brand")




    @staticmethod
    def validate_enum(value: str, enum_class: Type[Enum], field_name: str) -> str:
        """Converts and validates a string value against an Enum."""
        try:
            # Try to match the string to the Enum value.
            return enum_class(value)
        except ValueError:
            # If the value doesn't match, raise an error with allowed values.
            allowed_values = ", ".join(e.value for e in enum_class)
            raise ValueError(f"Invalid {field_name}: '{value}'. Allowed values: {allowed_values}")


    class Config:
        use_enum_values = True
        from_attributes = True
        extra = 'forbid'



class Truck_pydantic_model_response(Truck_pydantic_model):
    truck_id: uuid.UUID = Field()




from driver.driver_models import Driver