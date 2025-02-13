from fastapi import APIRouter , Depends, Body, HTTPException, Query,status
from sqlalchemy.exc import IntegrityError
from db.db_connection import get_db
from .driver_models import Driver, Driver_pydantic_model, Driver_update_pydantic_model
from sqlalchemy.orm import Session, joinedload
from typing import Annotated
from truck.truck_models import Truck
from sqlalchemy import func, and_, case, func, not_
import uuid



router= APIRouter(prefix='/driver', tags=['this are the driver routes'])


@router.post('/create')
async def create_driver(
    driver:Annotated[Driver_pydantic_model,Body()],
    session:Session=Depends(get_db)
    )-> Driver_pydantic_model:

    try:
        with session.begin():
            driver = Driver(**driver.model_dump())
            session.add(driver)
            session.commit()
            return driver
    except IntegrityError as e:
        raise HTTPException(status_code=400,detail=f'an error occured: {str(e.orig)}')
    except Exception as e:
        raise HTTPException(status_code=500,detail=f'an error occured: {str(e)}')

 

 

@router.get('/get_drivers')
async def get_drivers(session: Session = Depends(get_db)) -> list[dict]:
    try:
  
        drivers = session.query(Driver).join(Truck).options(joinedload(Driver.truck)).all()

        data = [
            {'driver':driver.name,
            'truck_distance':driver.truck.distance_driven,
            'truck_registation':driver.truck.number_plate,
            'address':driver.address,
            'driver_id':driver.driver_id
            }
            for driver in drivers
                ]
        return data
    except Exception as e:
        raise HTTPException(status_code=500,detail=f'an error occured: {str(e)}')



@router.get('/filter_drivers')
async def filter_trucks(
    session:Session=Depends(get_db),
    # )  ->list[Driver_pydantic_model]:
    ):
    try:
      
        """learning how to work with some """
        """filter drivers by name that starts with case insensitive letters """
        drivers = session.query(Driver).filter(Driver.name.ilike('Gi%')).all()

        """filter drivers by name that contains case sensitive letters """
        drivers = session.query(Driver).filter(Driver.name.contains('gig')).all()
        """"""
        """get the sum of all the distance driven"""
        drivers = session.query(func.sum(Truck.distance_driven)).scalar()
        """get the sum only if the driver has less than 600000 km"""
        drivers = (session.query(
            func.sum(Truck.distance_driven))
            .join(Driver) 
            .filter(
                and_(
                Truck.distance_driven<=600000,
                Driver.name.ilike('%gi%')                    
                    )
                ).scalar())
        # return drivers
        """annotation new_distance that adds 1000 to distance_driven """
        trucks = session.query(Truck.distance_driven,
            (Truck.distance_driven + 1000).label('new_distance')
            )
        new_data= [
        {'new_distance':truck.distance_driven,'old_distance':truck.new_distance}
        for truck in trucks
            ]
        # return new_data
        
        """give labels to drivers upon distance driven"""
        drivers = session.query(
            Driver.name,
            case(
                (Truck.distance_driven <= 500000, 'lazy'),
                (Truck.distance_driven > 500000, 'hard working'),
                else_='Unknown',
            ).label('status')  
        ).outerjoin(Truck).all()
        # return drivers

        annotation = [
            {'driver_name':driver.name,'label':driver.status}
            for driver in drivers
            ]
        # return annotation
        """get the all the name of the drivers that registration plate starts with GL"""
        drivers_name = (
                        session.query(Driver)
                        .join(Truck)
                        .filter(Truck.number_plate.ilike('GL%'))
                        .order_by(Driver.date_of_birth.desc())
                        .all()
            )
        drivers_registration = [{
            'driver_name':driver.name                
            }
            for driver in drivers_name
            ]
        # return drivers_registration
        """count all the drivers"""
        number_of_drivers = (
            session.query(
            func.count(Driver.driver_id))
            .scalar()
            )

        # return number_of_drivers
        """total number of km driven"""
        total_km = (
            session.query(
            func.sum(Truck.distance_driven))
            .scalar()
            )
        # return total_km
        # the name of the drivers that have driven over 500000km
        query = (
            session.query(Driver.name)
            .filter(
                and_(
                Truck.distance_driven>=500000),
                not_(Driver.name == 'dumitru') 
                )
            .all()
            ) 
        names = [{'driver_name':driver.name}for driver in query]
        # return names
        # distance driven * 2
        annotate_drivers = (
                session.query(
                    (Truck.distance_driven).label("old_distance"),
                    (Truck.distance_driven * 2 ).label('distance_doubled'))
                    .all()
            )
        print(annotate_drivers)
        data = [{
            "old distance":driver.old_distance,
            "new distance":driver.distance_doubled
            }
                for driver in annotate_drivers]
        return data 

    except Exception as e:
        raise HTTPException(status_code=500,detail=f'an error occured: {str(e)}')





@router.get('/filter_drivers_join')
async def filter_trucks(
    session:Session=Depends(get_db),
    ) :

    try:
     
        """get the sum only if the driver has less than 500000 km"""
        query = (
            session.query(Driver)
            .filter(Truck.distance_driven < 500000)
            .options(joinedload(Driver.truck))  # Ensure truck is eagerly loaded
            .all()
            )
        drivers = [
            {"driver name":driver.name,"driver_email":driver.email}
            for driver in query]
        return drivers
    except Exception as e:
        raise HTTPException(status_code=500,detail=f'an error occured: {str(e)}')



 





@router.get('/filter_drivers_by_address')
async def filter_trucks(
    address:Annotated[str,Query()],
    number_plate:Annotated[str,Query()],
    session:Session=Depends(get_db),
    )  ->list[Driver_pydantic_model]:
    # ):
    try:
            # return drivers_registration
        """query drivers by number plate and address"""
        query = (
            session.query(Driver)
            .join(Truck)
            .options(joinedload(Driver.truck))
            .filter(
                and_(Truck.number_plate.ilike(f'%{number_plate}%'),
                    Driver.address.ilike(f'%{address}%')
                    )
            ).all()
        )
        return query


    except Exception as e:
        raise HTTPException(status_code=500,detail=f'an error occured: {str(e)}')




"""remove one driver"""
@router.delete('/remove_driver')
async def remove_driver(
    driver_id:Annotated[str,uuid],
    session:Session=Depends(get_db)
    )->dict:
    try:
        with session.begin():
            valid_uuid = uuid.UUID(driver_id)
            driver = session.get(Driver,valid_uuid)
            if driver is None:
                raise HTTPException(status_code=400,detail=f'no driver with the id {driver_id} found.')
            session.delete(driver)
            return {'status code':f'{status.HTTP_204_NO_CONTENT}','success':'user removed'}
    except ValueError:
        raise HTTPException(status_code=400, detail='Invalid uuid format')
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500,detail=f'an error occured: {str(e)}')








"""update partial data of  a driver"""
@router.patch('/partial_update')
async def remove_driver(
    driver_id:Annotated[str,uuid],
    driver_name:Driver_update_pydantic_model,
    session:Session=Depends(get_db)
    )->Driver_pydantic_model:
    try:
        with session.begin():
            valid_uuid = uuid.UUID(driver_id)
            driver = session.get(Driver,valid_uuid)
            if driver is None:
                raise HTTPException(status_code=400,detail=f'no driver with the id {driver_id} found.')
            driver.name = driver_name.name
            session.commit()
            return driver
    except IntegrityError:
        raise HTTPException(status_code=400, detail=f'user name already exists')
    except ValueError:
        raise HTTPException(status_code=400, detail='Invalid uuid format')
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500,detail=f'an error occured: {str(e)}')



"""total update data of a driver"""
@router.put('/complete_update')
async def remove_driver(
    driver_id:Annotated[str,uuid],
    driver_name:Driver_pydantic_model,
    session:Session=Depends(get_db)
    )->Driver_pydantic_model:
    try:
        with session.begin():
            valid_uuid = uuid.UUID(driver_id)
            driver = session.get(Driver,valid_uuid)
            if driver is None:
                raise HTTPException(status_code=400,detail=f'no driver with the id {driver_id} found.')
            for key, value in driver_name.model_dump().items():
                setattr(driver, key, value)
            session.commit()
            return driver
    except IntegrityError as e:
        raise HTTPException(status_code=400, detail=f'{str(e.orig)}')
    except ValueError:
        raise HTTPException(status_code=400, detail='Invalid uuid format')
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500,detail=f'an error occured: {str(e)}')









