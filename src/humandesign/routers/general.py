from fastapi import APIRouter, Query, HTTPException, Depends
from fastapi.responses import JSONResponse, Response
from timezonefinder import TimezoneFinder
import json

from .. import features as hd
from .. import hd_constants
from ..utils import serialization as cj
from ..services import chart_renderer as chart
from ..services.geolocation import get_latitude_longitude
from ..dependencies import verify_token
from ..utils.date_utils import clean_birth_date_to_iso, clean_create_date_to_iso

router = APIRouter()

@router.get("/calculate")
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
    # 1. Validate andcollect input
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
            "birth_date": clean_birth_date_to_iso(single_result[9], hours),
            "create_date": clean_create_date_to_iso(single_result[10]),
            "birth_place": place,
            "energy_type": single_result[0],
            "inner_authority": single_result[1],
            "inc_cross": single_result[2],
            "profile": single_result[4],
            "active_chakras": single_result[7],
            "inactive_chakras": set(hd_constants.CHAKRA_LIST) - set(single_result[7]),
            "definition": "{}".format(single_result[5]),
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
        "channels": channels_output,
        "gates": gates_output
    }
    return JSONResponse(content=final_result)

@router.get("/bodygraph")
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
            "birth_date": clean_birth_date_to_iso(single_result[9], hours),
            "create_date": clean_create_date_to_iso(single_result[10]),
            "energy_type": single_result[0],
            "inner_authority": single_result[1],
            "inc_cross": single_result[2],
            "profile": single_result[4],
            "active_chakras": single_result[7],
            "inactive_chakras": set(hd_constants.CHAKRA_LIST) - set(single_result[7]),
            "definition": "{}".format(single_result[5]),
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
