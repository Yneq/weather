from fastapi import APIRouter
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from models.CityName import CityName
import httpx
import os

router = APIRouter()

load_dotenv()
CWB_API_KEY = os.getenv('CWB_API_KEY')

API_URL = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-D0047-091"

@router.get("/weekly_weather/{city_name}", responses={
    200: {
        "description": "The weather forecast for a specific city.",
        "content": {
            "application/json": {
                "example": {
                    "city":"臺北市",
                    "weather":[
                        {
                            "date":"2024-07-18",
                            "time":"晚上",
                            "MaxT":"34",
                            "MinT":"29",
                            "RH":"64",
                            "Wx":"04",
                            "PoP12h":"59%"
                        },
                        {
                            "date":"2024-07-19",
                            "time":"白天",
                            "MaxT":"34",
                            "MinT":"29",
                            "RH":"64",
                            "Wx":"02",
                            "PoP12h":"59%"
                        }
                    ]
                }
            }
        }
    },
    404: {
        "description": "City not found",
        "content": {
            "application/json": {
                "example": {
                    "message": "找不到 {city_name} 的一週天氣資料"
                }
            }
        }
    },
    500: {
        "description": "Server error",
        "content": {
            "application/json": {
                "example": {
                    "message": "Internal server error."
                }
            }
        }
    }
})
async def get_city_weekly_weather(city_name: str):
    try:
        if city_name in CityName.get_city_names():
            params = {
                "sort": "time",
                "Authorization": CWB_API_KEY,
                "locationName": city_name,
                "limit": 14,
                "elementName": ["MinT", "MaxT", "RH", "Wx", "PoP12h"],
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(API_URL, params=params)

            if response.status_code == 200:
                data = response.json()
                return_data = arrange_weather_data(city_name, data)
                print(data)
                return JSONResponse(status_code=200, content=return_data)
            elif response.status_code == 404:
                return JSONResponse(status_code=404, content={"message": f"找不到 {city_name} 的一週天氣資料"})
            else:
                return JSONResponse(status_code=response.status_code, content={"message": "Error fetching data from API."})

        else:
            return JSONResponse(status_code=404, content={"message": f"找不到 {city_name} 的一週天氣資料"})

    except Exception as e:
        import logging
        logging.exception(e)
        return JSONResponse(status_code=500, content={"message": "Internal server error."})


# 整理資料讓前端好辦事
def arrange_weather_data(city_name: str, data: dict):
    response = {
        "city": city_name,
        "weather": []
    }

    if data.get("success") == "true" and "records" in data:
        locations = data["records"].get("locations", [])

        for location in locations:
            for loc in location.get("location", []):
                if loc.get("locationName") == city_name:
                    weather_elements = loc.get("weatherElement", [])
                    for weather_element in weather_elements:
                        element_name = weather_element.get("elementName")

                        for time_data in weather_element.get("time", []):
                            start_time = time_data.get("startTime")
                            date, time = start_time.split(" ")

                            weather_info = next((item for item in response["weather"] if item["date"] == date and item["time"] == ("白天" if "06:00:00" <= time < "18:00:00" else "晚上")), None)
                            if not weather_info:
                                weather_info = {
                                    "date": date,
                                    "time": "白天" if "06:00:00" <= time < "18:00:00" else "晚上",
                                    "MaxT": "",
                                    "MinT": "",
                                    "RH": "",
                                    "Wx": "",
                                    "PoP12h": ""
                                }
                                response["weather"].append(weather_info)

                            element_value = time_data.get("elementValue", [{}])[0].get("value")
                            if element_name == "MaxT":
                                weather_info["MaxT"] = element_value
                            elif element_name == "MinT":
                                weather_info["MinT"] = element_value
                            elif element_name == "RH":
                                weather_info["RH"] = element_value
                            elif element_name == "Wx":
                                weather_info["Wx"] = time_data.get("elementValue", [{}])[1].get("value")
                            elif element_name == "PoP12h":
                                weather_info["PoP12h"] = "-" if element_value == " " else element_value + "%"

    return response
