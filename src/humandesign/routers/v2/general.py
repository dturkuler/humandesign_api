from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
import json

from ... import features as hd
from ... import hd_constants
from ...utils import serialization as cj
from ...services.geolocation import get_latitude_longitude, tf
from ...dependencies import verify_token
from ...utils.date_utils import clean_birth_date_to_iso, clean_create_date_to_iso
from ...schemas.v2.calculate import CalculateRequestV2, CalculateResponseV2, GeneralSectionV2, GateV2
from ...services.masking import OutputMaskingService

router = APIRouter(prefix="/v2", tags=["v2"])

@router.post("/calculate", response_model=CalculateResponseV2, response_model_exclude_none=True)
def calculate_hd_v2(
    request: CalculateRequestV2,
    authorized: bool = Depends(verify_token)
):
    # 1. Validate and collect input
    birth_time = (request.year, request.month, request.day, request.hour, request.minute, request.second)

    # 2. Geocode and timezone
    try:
        latitude, longitude = request.latitude, request.longitude
        if latitude is None or longitude is None:
            latitude, longitude = get_latitude_longitude(request.place)
            
        if latitude is not None and longitude is not None:
            if "/" in request.place:
                zone = request.place
            else:
                zone = tf.timezone_at(lat=latitude, lng=longitude) or 'Etc/UTC'
        else:
            raise HTTPException(status_code=400, detail=f"Geocoding failed for place: '{request.place}'")
            
        hours = hd.get_utc_offset_from_tz(birth_time, zone)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error determining timezone or offset: {str(e)}")

    # 3. Prepare timestamp
    timestamp = tuple(list(birth_time) + [float(hours)])

    # 4. Calculate Human Design Features
    try:
        single_result = hd.calc_single_hd_features(timestamp, report=False, channel_meaning=False, day_chart_only=False)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating Human Design features: {str(e)}")

    # 5. Additional Calculations (Age, Zodiac)
    from ...utils import astrology
    from ...utils import date_utils
    
    age = date_utils.calculate_age(birth_time)
    sun_lon = single_result[6]['lon'][0]
    zodiac_sign = astrology.get_zodiac_sign(sun_lon)

    # 6. Format Data for V2 Response
    try:
        # Build General Section
        general_data = {
            "birth_date": clean_birth_date_to_iso(single_result[9], hours),
            "create_date": clean_create_date_to_iso(single_result[10]),
            "birth_place": request.place,
            "energy_type": single_result[0],
            "inner_authority": single_result[1],
            "inc_cross": f"{single_result[2]}", # Simplified for now
            "profile": f"{single_result[4][0]}/{single_result[4][1]}",
            "active_chakras": list(single_result[7]),
            "inactive_chakras": list(set(hd_constants.CHAKRA_LIST) - set(single_result[7])),
            "definition": "{}".format(single_result[5]),
            "variables": single_result[11],
            "age": age,
            "zodiac_sign": zodiac_sign,
            "gender": request.gender or "male",
            "islive": request.islive if request.islive is not None else True
        }
        
        # Build Gates Section
        raw_gates = single_result[6]
        gates_v2 = {}
        for i, p_name in enumerate(raw_gates['planets']):
            gates_v2[p_name] = GateV2(
                gate=raw_gates['gate'][i],
                line=raw_gates['line'][i],
                color=raw_gates['color'][i],
                tone=raw_gates['tone'][i],
                base=raw_gates['base'][i],
                lon=raw_gates['lon'][i]
            )
            
        # Build Channels Section
        channels_json_str = cj.channelsJSON(single_result[8], False)
        channels_v2 = json.loads(channels_json_str).get("Channels", [])

        # Construct Full Response (Unmasked)
        full_response = {
            "general": general_data,
            "gates": gates_v2,
            "channels": channels_v2,
            "mechanics": None, # Placeholder for Phase 2
            "advanced": None   # Placeholder for Phase 3
        }
        
        # Apply Masking
        masked_response = OutputMaskingService.apply_mask(
            full_response, 
            include=request.include, 
            exclude=request.exclude
        )
        
        return masked_response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing V2 results: {str(e)}")
