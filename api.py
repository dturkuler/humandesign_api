from fastapi import FastAPI, Query, HTTPException, Depends
from fastapi.responses import JSONResponse, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import hd_features as hd
import hd_constants
import convertJSON as cj
import chart 
from geocode import get_latitude_longitude
from timezonefinder import TimezoneFinder
import json


app = FastAPI(title="Human Design API")

import os
from dotenv import load_dotenv

# --- Load environment variables from .env with debug output ---
env_path = os.path.join(os.path.dirname(__file__), ".env")
# print(f"[DEBUG] Attempting to load .env from: {env_path}")
if os.path.exists(env_path):
    with open(env_path, "r") as f:
        pass
        # print("[DEBUG] .env contents:")
        # print(f.read())
else:
    pass
    # print("[DEBUG] .env file not found at expected location!")

load_dotenv(dotenv_path=env_path, override=True)
TOKEN = os.getenv("HD_API_TOKEN")
# print(f"[DEBUG] Loaded HD_API_TOKEN: '{TOKEN}'")  # Debug print for troubleshooting
if not TOKEN:
    raise RuntimeError("HD_API_TOKEN environment variable is not set. Please set it before running the API or add it to your .env file.")
security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != TOKEN:
        raise HTTPException(status_code=401, detail="Invalid or missing authentication token.")
    return True

@app.get("/calculate")
def calculate_hd(
    year: int = Query(..., description="Birth year"),
    month: int = Query(..., description="Birth month"),
    day: int = Query(..., description="Birth day"),
    hour: int = Query(..., description="Birth hour"),
    minute: int = Query(..., description="Birth minute"),
    second: int = Query(0, description="Birth second (optional, default 0)"),
    place: str = Query(..., description="Birth place (city, country)"),
    authorized: bool = Depends(verify_token)
):
    # 1. Validate and collect input
    birth_time = (year, month, day, hour, minute, second)

    # 2. Geocode and timezone
    try:
        latitude, longitude = get_latitude_longitude(place)
        if latitude is not None and longitude is not None:
            tf = TimezoneFinder()
            zone = tf.timezone_at(lat=latitude, lng=longitude)
            if not zone:
                zone = 'Etc/UTC'
        else:
            raise HTTPException(status_code=400, detail=f"Geocoding failed for place: '{place}'. Please check the place name or try a different format.")
        hours = hd.get_utc_offset_from_tz(birth_time, zone)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error determining timezone or offset: {str(e)}")

    # 3. Prepare timestamp
    timestamp = tuple(list(birth_time) + [int(hours)])

    # 4. Calculate Human Design Features
    try:
        single_result = hd.calc_single_hd_features(timestamp, report=False, channel_meaning=False, day_chart_only=False)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating Human Design features: {str(e)}")

    # 5. Format Data for JSON Output
    try:
        data = {
            "birth_date": single_result[9],
            "create_date": single_result[10],
            "energie_type": single_result[0],
            "inner_authority": single_result[1],
            "inc_cross": single_result[2],
            "profile": single_result[4],
#            "active_chakras": [hd_constants.CHAKRA_NAMES_MAP.get(chakra, chakra) for chakra in single_result[7]],
            "active_chakras": single_result[7],
            "inactive_chakras": set(hd_constants.CHAKRA_LIST) - set(single_result[7]),
            "split": "{}".format(single_result[5]),
            "variables": {
                'right_up': 'right',
                'right_down': 'left',
                'left_up': 'right',
                'left_down': 'right'
            }
        }
        general_json_str = cj.general(data)
        gates_json_str = cj.gatesJSON(single_result[6])
        channels_json_str = cj.channelsJSON(single_result[8], False)
        general_output = json.loads(general_json_str)
        gates_output = json.loads(gates_json_str)
        channels_output = json.loads(channels_json_str)
    except IndexError as e:
        raise HTTPException(status_code=500, detail=f"Error processing calculation results: Missing expected data at index {e}")
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Internal error generating JSON output: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error processing results: {e}")

    final_result = {
        "general": general_output,
        "gates": gates_output,
        "channels": channels_output
    }
    return JSONResponse(content=final_result)

@app.get("/bodygraph")
def get_bodygraph_image(
    year: int = Query(..., description="Birth year"),
    month: int = Query(..., description="Birth month"),
    day: int = Query(..., description="Birth day"),
    hour: int = Query(..., description="Birth hour"),
    minute: int = Query(..., description="Birth minute"),
    second: int = Query(0, description="Birth second (optional, default 0)"),
    place: str = Query(..., description="Birth place (city, country)"),
    fmt: str = Query("png", description="Image format: png or svg"),
    authorized: bool = Depends(verify_token)
):
    # Reuse the logic? Ideally we'd refactor, but for now let's reuse the internal logic by calling a helper or duplicating.
    # Duplication for safety in this context:
    
    # 1. Validate and collect input
    birth_time = (year, month, day, hour, minute, second)

    # 2. Geocode and timezone
    try:
        latitude, longitude = get_latitude_longitude(place)
        if latitude is not None and longitude is not None:
            tf = TimezoneFinder()
            zone = tf.timezone_at(lat=latitude, lng=longitude)
            if not zone:
                zone = 'Etc/UTC'
        else:
            raise HTTPException(status_code=400, detail=f"Geocoding failed for place: '{place}'. Please check the place name or try a different format.")
        hours = hd.get_utc_offset_from_tz(birth_time, zone)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error determining timezone or offset: {str(e)}")

    # 3. Prepare timestamp
    timestamp = tuple(list(birth_time) + [int(hours)])

    # 4. Calculate Human Design Features
    try:
        single_result = hd.calc_single_hd_features(timestamp, report=False, channel_meaning=False, day_chart_only=False)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating Human Design features: {str(e)}")

    # 5. Format Data for JSON Output (Required for Chart)
    try:
        data = {
            "birth_date": single_result[9],
            "create_date": single_result[10],
            "energie_type": single_result[0],
            "inner_authority": single_result[1],
            "inc_cross": single_result[2],
            "profile": single_result[4],
            "active_chakras": single_result[7],
            "inactive_chakras": set(hd_constants.CHAKRA_LIST) - set(single_result[7]),
            "split": "{}".format(single_result[5]),
            "variables": {
                'right_up': 'right',
                'right_down': 'left',
                'left_up': 'right',
                'left_down': 'right'
            }
        }
        general_json_str = cj.general(data)
        gates_json_str = cj.gatesJSON(single_result[6])
        channels_json_str = cj.channelsJSON(single_result[8], False)
        
        general_output = json.loads(general_json_str)
        gates_output = json.loads(gates_json_str)
        channels_output = json.loads(channels_json_str)
        
        final_result = {
            "general": general_output,
            "gates": gates_output,
            "channels": channels_output
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error formatting data for chart: {e}")
        
    # 6. Generate Image
    try:
        img_bytes = chart.generate_bodygraph_image(final_result, fmt=fmt)
        media_type = "image/svg+xml" if fmt == 'svg' else "image/png"
        return Response(content=img_bytes, media_type=media_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating chart image: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
