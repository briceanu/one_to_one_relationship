from fastapi import APIRouter, Depends, Body, HTTPException
from db.db_connection import get_db
from sqlalchemy.orm import Session
from .truck_models import Truck_pydantic_model, Truck, Truck_pydantic_model_response
from typing import Annotated
from sqlalchemy.exc import IntegrityError



router= APIRouter(prefix='/truck',tags=['this are the routes for trucks'])

@router.post('/create')
async def create_truck(
    truck:Annotated[Truck_pydantic_model,Body()],
    session:Session=Depends(get_db),
    ) -> Truck_pydantic_model_response:
    try:
        with session.begin():
            truck = Truck(**truck.model_dump())
            session.add(truck)
            session.commit()
            return truck
    except IntegrityError:
        raise HTTPException(status_code=400,detail='registration plate already used.')
    except Exception as e:
        raise HTTPException(status_code=500,detail=f'an error occured: {str(e)}')


@router.get('/get_trucks')
async def get_trucks(
    session:Session=Depends(get_db),
    )  ->list[Truck_pydantic_model_response]:
    try:
        with session.begin():
            truck = session.query(Truck).all()
            return truck
    except Exception as e:
        raise HTTPException(status_code=500,detail=f'an error occured: {str(e)}')

