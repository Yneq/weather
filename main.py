from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from controllers import cityname_controller, daily_weather_controller, weekly_weather_controller, weekly_city_weather_controller
from models.Bot import loop
import asyncio

app = FastAPI()
running = True

# 前端同仁自行調整資料存放位置
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", include_in_schema=False)
async def index(request: Request):
  return FileResponse("./static/index.html", media_type="text/html")


@app.get("/city/{city}", include_in_schema=False)
async def index_without_district(request: Request, city: str):
    return FileResponse("./static/city.html", media_type="text/html")


@app.get("/city/{city}/{district}", include_in_schema=False)
async def index_with_district(request: Request, city: str, district: str):
    return FileResponse("./static/district.html", media_type="text/html")




# 後端同仁自行設定路由與 Controller 名稱
app.include_router(cityname_controller.router, tags=["cityname"], prefix="/api/v1")
app.include_router(daily_weather_controller.router, tags=["daily_weather"], prefix="/api/v1")
app.include_router(weekly_weather_controller.router, tags=["weekly_weather"], prefix="/api/v1")
app.include_router(weekly_city_weather_controller.router, tags=["weekly_city_weather"], prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
  global running
  running = True
  asyncio.create_task(loop(lambda:running))

@app.on_event("shutdown")
async def shutdown_event():
  global running
  running = False