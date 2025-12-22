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
import tomllib
import os

# --- Read version from pyproject.toml ---
try:
    with open(os.path.join(os.path.dirname(__file__), "pyproject.toml"), "rb") as f:
        project_data = tomllib.load(f)
        __version__ = project_data["project"]["version"]
except FileNotFoundError:
    __version__ = "0.0.0"

app = FastAPI(title="Human Design API", version=__version__)

import os
from dotenv import load_dotenv

# --- Load environment variables from .env ---
env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=env_path, override=True)

TOKEN = os.getenv("HD_API_TOKEN")
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
            "energy_type": single_result[0],
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
    fmt: str = Query("png", description="Image format: png, svg, jpg/jpeg"),
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

    # 5. Format Data for JSON Output (Required for Chart)
    try:
        data = {
            "birth_date": single_result[9],
            "create_date": single_result[10],
            "energy_type": single_result[0],
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
        if fmt == 'svg':
            media_type = "image/svg+xml"
        elif fmt in ['jpg', 'jpeg']:
            media_type = "image/jpeg"
        else:
            media_type = "image/png"
            
        return Response(content=img_bytes, media_type=media_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating chart image: {e}")


# --- Helper to process transit data (combines existing logic) ---
def process_transit_data(transit_date_timestamp, birth_timestamp):
    # 1. Calculate birth chart to get natal features (prs + des)
    birth_features = hd.calc_single_hd_features(birth_timestamp, report=False, channel_meaning=True, day_chart_only=False)
    natal_gate_dict = birth_features[6]

    # 2. Calculate day chart (transit features only)
    day_gate_dict = hd.calc_single_hd_features(transit_date_timestamp, day_chart_only=True)
    
    # 3. Prepare composite dict: Natal (prs+des) + Transit (day chart)
    # The composite analysis expects both natal and a day chart to be concatenated.
    # We explicitly select keys to merge to avoid KeyErrors (e.g., 'ch_gate')
    keys_to_merge = ["label", "planets", "lon", "gate", "line", "color", "tone", "base"]
    composite_dict = {
        key: natal_gate_dict[key] + day_gate_dict[key] 
        for key in keys_to_merge if key in natal_gate_dict and key in day_gate_dict
    }
    
    # 4. Analyze composite features
    active_channels_dict, active_chakras = hd.get_channels_and_active_chakras(composite_dict, meaning=True)
    typ = hd.get_typ(active_channels_dict, active_chakras) # The resulting 'transit' type
    auth = hd.get_auth(active_chakras, active_channels_dict) # The resulting 'transit' authority
    
    # 5. Get comparison data (New and Duplicated Channels/Chakras)
    # We must mock the input for composite_chakras_channels.
    persons_dict = {
        "natal": birth_timestamp,
        "transit": transit_date_timestamp # We treat transit as another "person" for comparison
    }
    # This comparison highlights what is new *to the combination*
    new_channels, duplicated_channels, new_chakras, comp_chakras = hd.composite_chakras_channels(
        persons_dict, "natal", "transit") 
    
    # 6. Structure output
    return {
        "transit_date": transit_date_timestamp,
        "composite_type": typ,
        "composite_authority": auth,
        "new_defined_channels": list(zip(new_channels["gate"], new_channels["ch_gate"])),
        "new_channel_meanings": list(new_channels["meaning"]),
        "new_defined_centers": list(new_chakras),
        "total_defined_centers": len(comp_chakras),
        "raw_transit_gates": day_gate_dict
    }


@app.get("/transits/solar_return")
def get_solar_return(
    year: int = Query(..., description="Birth year"),
    month: int = Query(..., description="Birth month"),
    day: int = Query(..., description="Birth day"),
    hour: int = Query(..., description="Birth hour"),
    minute: int = Query(0, description="Birth minute (default 0)"),
    second: int = Query(0, description="Birth second (optional, default 0)"),
    place: str = Query(..., description="Birth place (city, country)"),
    sr_year_offset: int = Query(0, description="Calculate Solar Return for X years after birth. 0 is the current SR."),
    authorized: bool = Depends(verify_token)
):
    # Same geocoding/timezone logic as calculate_hd
    latitude, longitude = get_latitude_longitude(place)
    if latitude is None or longitude is None:
        raise HTTPException(status_code=400, detail=f"Geocoding failed for place: '{place}'")
    tf = TimezoneFinder()
    zone = tf.timezone_at(lat=latitude, lng=longitude) or 'Etc/UTC'
    birth_time = (year, month, day, hour, minute, second)
    hours = hd.get_utc_offset_from_tz(birth_time, zone)
    birth_timestamp = tuple(list(birth_time) + [int(hours)])

    # Calculate Solar Return Date
    try:
        instance = hd.hd_features(*birth_timestamp)
        sr_utc_date_tuple = instance.get_solar_return_date(sr_year_offset)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating Solar Return date: {str(e)}")

    # Format the SR date for transit calculation
    sr_year, sr_month, sr_day, sr_hour, sr_minute, sr_second = sr_utc_date_tuple
    # Re-use the birth location's offset for the SR chart (standard HD practice)
    sr_timestamp = (int(sr_year), int(sr_month), int(sr_day), int(sr_hour), int(sr_minute), int(sr_second), int(hours))
    
    # Calculate the full composite chart at the SR moment
    sr_composite_data = process_transit_data(sr_timestamp, birth_timestamp)
    
    return {
        "solar_return_year": sr_year_offset,
        "solar_return_utc_date": f"{int(sr_year)}-{int(sr_month):02d}-{int(sr_day):02d} {int(sr_hour):02d}:{int(sr_minute):02d}:{int(sr_second):02d}",
        "sr_chart_analysis": sr_composite_data
    }


@app.get("/transits/daily")
def get_daily_transit(
    year: int = Query(..., description="Birth year"),
    month: int = Query(..., description="Birth month"),
    day: int = Query(..., description="Birth day"),
    hour: int = Query(..., description="Birth hour"),
    minute: int = Query(0, description="Birth minute (default 0)"),
    second: int = Query(0, description="Birth second (optional, default 0)"),
    place: str = Query(..., description="Birth place (city, country)"),
    transit_year: int = Query(..., description="Transit year to analyze"),
    transit_month: int = Query(..., description="Transit month to analyze"),
    transit_day: int = Query(..., description="Transit day to analyze"),
    authorized: bool = Depends(verify_token)
):
    # Geocoding/timezone for the BIRTH location
    latitude, longitude = get_latitude_longitude(place)
    if latitude is None or longitude is None:
        raise HTTPException(status_code=400, detail=f"Geocoding failed for place: '{place}'")
    tf = TimezoneFinder()
    zone = tf.timezone_at(lat=latitude, lng=longitude) or 'Etc/UTC'
    birth_time = (year, month, day, hour, minute, second)
    hours = hd.get_utc_offset_from_tz(birth_time, zone)
    birth_timestamp = tuple(list(birth_time) + [int(hours)])

    # Transit timestamp (uses Birth location's local time/offset for the analysis moment)
    transit_time = (transit_year, transit_month, transit_day, birth_time[3], birth_time[4], birth_time[5])
    transit_timestamp = tuple(list(transit_time) + [int(hours)])

    # Calculate the composite chart at the transit moment
    composite_data = process_transit_data(transit_timestamp, birth_timestamp)

    return {
        "transit_date": f"{transit_year}-{transit_month:02d}-{transit_day:02d}",
        "transit_time_at_birth_location": f"{birth_time[3]:02d}:{birth_time[4]:02d}",
        "analysis": composite_data
    }

from composite_handler import process_composite_matrix
from pydantic import BaseModel, Field, validator
from typing import Dict, List, Union
from fastapi import Body

# ... (Previous code) ...

# Input Model
class PersonInput(BaseModel):
    place: str = Field(..., min_length=1, description="Place of birth (City, Country)")
    year: Union[int, str] = Field(..., description="Birth year (1800-2100)")
    month: Union[int, str] = Field(..., description="Birth month (1-12)")
    day: Union[int, str] = Field(..., description="Birth day (1-31)")
    hour: Union[int, str] = Field(..., description="Birth hour (0-23)")
    minute: Union[int, str] = Field(..., description="Birth minute (0-59)")

    @validator('year', 'month', 'day', 'hour', 'minute', pre=True)
    def parse_int(cls, v):
        if isinstance(v, str):
            if not v.strip():
                raise ValueError("Empty string not allowed")
            return int(v)
        return v

    @validator('year')
    def validate_year_range(cls, v):
        if not (1800 <= v <= 2100):
            raise ValueError(f"Year {v} must be between 1800 and 2100")
        return v
    
    @validator('month')
    def validate_month_range(cls, v):
        if not (1 <= v <= 12):
            raise ValueError(f"Month {v} must be between 1 and 12")
        return v
        
    @validator('hour')
    def validate_hour_range(cls, v):
         if not (0 <= v <= 23):
            raise ValueError(f"Hour {v} must be between 0 and 23")
         return v

    @validator('minute')
    def validate_minute_range(cls, v):
         if not (0 <= v <= 59):
            raise ValueError(f"Minute {v} must be between 0 and 59")
         return v

    @validator('day')
    def validate_day_of_month(cls, v, values):
        # v is already int due to parse_int
        year = values.get('year')
        month = values.get('month')
        if year is None or month is None or not isinstance(year, int) or not isinstance(month, int):
            # If previous validations failed, skip complex logic
            return v
        
        if not (1 <= v <= 31):
             raise ValueError(f"Day {v} must be between 1 and 31")

        # Standard days per month
        days_in_month = {
            1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30,
            7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31
        }
        
        # Leap year check
        if month == 2 and (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)):
            days_in_month[2] = 29
            
        if v > days_in_month.get(month, 31):
             raise ValueError(f"Invalid day {v} for month {month} in year {year}")
        return v


@app.post("/compmatrix")
def get_composite_matrix(
    inputs: Dict[str, PersonInput] = Body(
        ...,
        example={
            "person1": {
                "place": "Berlin, Germany",
                "year": 1985,
                "month": 6,
                "day": 15,
                "hour": 14,
                "minute": 30
            },
            "person2": {
                "place": "Munich, Germany",
                "year": 1988,
                "month": 11,
                "day": 22,
                "hour": 9,
                "minute": 15
            }
        },
        description="Dictionary of people where keys are names (e.g., person1, person2) and values are birth details."
    ),
    authorized: bool = Depends(verify_token)
):
    """
    Calculate Human Design features for multiple people and analyze their composite combinations (matrix).
    
    Input:
    {
        "person1": { "place": "City, Country", "year": 1990, "month": 1, "day": 1, "hour": 12, "minute": 0 },
        "person2": { ... }
    }
    """
    # 1. Validate Input (Implicitly done by Pydantic)
    if not inputs:
        raise HTTPException(status_code=400, detail="Input dictionary cannot be empty.")

    # 2. Process via Handler
    try:
        result = process_composite_matrix(inputs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing composite matrix: {str(e)}")

    return JSONResponse(content=result)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
