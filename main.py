from fastapi import FastAPI
from driver.driver_routes import router as driver_router
from truck.truck_routes import router as truck_router

app = FastAPI()


app.include_router(driver_router)
app.include_router(truck_router)