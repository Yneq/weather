from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
import os
import requests
from models.CityName import CityName
from dotenv import load_dotenv
import pytz

load_dotenv()

raw_utc = datetime.now(pytz.utc)
now = raw_utc.astimezone(pytz.timezone('Asia/Taipei')).replace(tzinfo=None).strftime("%Y-%m-%d")
url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001"
params = {
    "sort": "time",
    "timeFrom": f'{now}T00:00:00',
    # "timeTo": f"{next_day}T01:00:00",
}
headers = {"Authorization": os.getenv('CWB_API_KEY')}

router = APIRouter()
@router.get("/weather/all/all/daily", responses={
    200: {
        "description": "A JSONresponse containing all of today's weather information for the city. 美比資料",
        "content": {
            "application/json": {
                "example": {
                    "data": [  
                        {
                            '臺北市': {
                            'MinT': [
                                {
                                'start': '2024-07-17 12:00:00',
                                'end': '2024-07-17 18:00:00',
                                'para': [
                                    '33'
                                ]
                                },
                                {
                                'start': '2024-07-17 18:00:00',
                                'end': '2024-07-18 06:00:00',
                                'para': [
                                    '28'
                                ]
                                }
                            ],
                            'MaxT': [
                                {
                                'start': '2024-07-17 12:00:00',
                                'end': '2024-07-17 18:00:00',
                                'para': [
                                    '38'
                                ]
                                },
                                {
                                'start': '2024-07-17 18:00:00',
                                'end': '2024-07-18 06:00:00',
                                'para': [
                                    '33'
                                ]
                                }
                            ],
                            'briefDescription': [
                                {
                                'start': '2024-07-17 12:00:00',
                                'end': '2024-07-17 18:00:00',
                                'para': [
                                    '2',
                                    '晴時多雲'
                                ]
                                },
                                {
                                'start': '2024-07-17 18:00:00',
                                'end': '2024-07-18 06:00:00',
                                'para': [
                                    '2',
                                    '晴時多雲'
                                ]
                                }
                            ],
                            'PoP': [
                                {
                                'start': '2024-07-17 12:00:00',
                                'end': '2024-07-17 18:00:00',
                                'para': [
                                    '20'
                                ]
                                },
                                {
                                'start': '2024-07-17 18:00:00',
                                'end': '2024-07-18 06:00:00',
                                'para': [
                                    '20'
                                ]
                                }
                            ]
                            }
                        },  
                        {'新北市': {'MinT':[],'MaxT':[],'briefDescription':[],'PoP':[]}},
                        {'基隆市': {'MinT':[],'MaxT':[],'briefDescription':[],'PoP':[]}},
                ]
            }
        }
    }
},
    500: {
        "description": "Server error.",
        "content": {
            "application/json": {
                "example": {
                    "message": "Internal server error."
                }
            }
        }
    }
})
async def get_daily_weather_info(request: Request):
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()['records']['location']

            location_info = {}
            for n in range(len(data)):
                raw = data[n]
                locationName = raw['locationName']
                we = raw['weatherElement']

                min = we[2]['time']
                MinT = [{'start':n['startTime'],'end':n['endTime'],'para':[n['parameter']['parameterName']]} for n in min]
                max = we[4]['time']
                MaxT = [{'start':n['startTime'],'end':n['endTime'],'para':[n['parameter']['parameterName']]} for n in max]
                wx = we[0]['time']
                briefDescription = [{'start':n['startTime'],'end':n['endTime'],'para':[n['parameter']['parameterValue'],n['parameter']['parameterName']]} for n in wx]
                Po = we[1]['time']
                PoP = [{'start':n['startTime'],'end':n['endTime'],'para':[n['parameter']['parameterName']]} for n in Po]

                processed_data = {'MinT':MinT, 'MaxT':MaxT, 'briefDescription':briefDescription, 'PoP':PoP}
                location_info[locationName] = processed_data

            citylist = CityName.get_city_names()
            processed_location_info = [{n:location_info[n]} for n in citylist]
            return JSONResponse(status_code=200, content=processed_location_info)
        
        else:
            return JSONResponse(status_code=response.status_code, content=response.content.decode('utf-8'))

    except requests.exceptions.RequestException as e:
        return JSONResponse(status_code=500, content={"message": str(e)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": str(e)})
