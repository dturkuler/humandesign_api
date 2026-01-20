from fastapi import APIRouter, Body, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import Dict
from timezonefinder import TimezoneFinder
from .. import features as hd
from .. import hd_constants
from ..services.geolocation import get_latitude_longitude
from ..dependencies import verify_token
from ..schemas.input_models import PersonInput, PentaRequest
from ..schemas.response_models import CompMatrixResponse
from ..services.composite import process_composite_matrix, process_maia_matrix

router = APIRouter()

@router.post("/analyze/compmatrix")
def get_composite_matrix(
    inputs: Dict[str, PersonInput] = Body(
        ...,
        examples=[{
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
        }],
        description="Dictionary of people where keys are names (e.g., person1, person2) and values are birth details."
    ),
    authorized: bool = Depends(verify_token)
):
    """
    Calculate Human Design features for multiple people and analyze their composite combinations (matrix).
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

@router.post("/analyze/maiamatrix", response_model=CompMatrixResponse)
def get_maia_matrix(
    inputs: Dict[str, PersonInput] = Body(
        ...,
        examples=[{
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
        }],
        description="Dictionary of people for Professional Maia Relational Matrix analysis."
    ),
    authorized: bool = Depends(verify_token)
):
    """
    Calculate Professional Maia Relational Matrix (deep pairwise analysis).
    Includes connection types (Electromagnetic, etc.) and 9-0 classification codes.
    """
    if not inputs:
        raise HTTPException(status_code=400, detail="Input dictionary cannot be empty.")

    try:
        result = process_maia_matrix(inputs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing maia matrix: {str(e)}")

    return JSONResponse(content=result)

@router.post("/analyze/composite")
def analyze_composite(
    inputs: Dict[str, PersonInput] = Body(
        ...,
        examples=[{
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
        }],
        description="Dictionary of exactly 2 people for Composite analysis."
    ),
    authorized: bool = Depends(verify_token)
):
    """
    Calculate Composite Chart features for exactly 2 people.
    Exposes detailed pairwise composite logic including new and duplicated channels/chakras.
    """
    # Validation
    if len(inputs) != 2:
         raise HTTPException(status_code=400, detail="Composite analysis requires exactly 2 people.")

    persons_dict = {}
    names = list(inputs.keys())
    
    # Process inputs (Geocode & Timezone)
    for name, p_input in inputs.items():
        try:
            latitude, longitude = get_latitude_longitude(p_input.place)
            if latitude is None or longitude is None:
                 raise HTTPException(status_code=400, detail=f"Geocoding failed for {name} place: '{p_input.place}'")
            
            if "/" in p_input.place:
                zone = p_input.place
            else:
                tf = TimezoneFinder()
                zone = tf.timezone_at(lat=latitude, lng=longitude) or 'Etc/UTC'
            
            birth_time = (p_input.year, p_input.month, p_input.day, p_input.hour, p_input.minute, 0)
            hours = hd.get_utc_offset_from_tz(birth_time, zone)
            
            # Construct (Y,M,D,H,M,S,Offset)
            timestamp = (p_input.year, p_input.month, p_input.day, p_input.hour, p_input.minute, 0, hours)
            persons_dict[name] = timestamp
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing input for {name}: {str(e)}")

    # Call composite_chakras_channels
    try:
        new_channels_df, duplicated_channels_df, new_chakras, composite_chakras = hd.composite_chakras_channels(
            persons_dict, names[0], names[1]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in Composite calculation: {str(e)}")

    # Serialize Output
    def serialize_channels(df):
        if df.empty:
            return []
        # Convert DataFrame to list of dicts, keeping relevant columns
        return df[['gate', 'ch_gate', 'meaning']].to_dict(orient='records')

    # Helper to map chakra codes to names
    def map_chakras(chakra_list):
        return [
            hd_constants.CHAKRA_NAMES_MAP.get(c, c)
            for c in chakra_list
        ]

    return {
        "participants": names,
        "new_channels": serialize_channels(new_channels_df),
        "duplicated_channels": serialize_channels(duplicated_channels_df),
        "new_chakras": map_chakras(new_chakras),
        "composite_chakras": map_chakras(composite_chakras)
    }




@router.post("/analyze/penta")
def analyze_penta(
    request: PentaRequest = Body(
        ...,
        examples=[{
            "group_type": "family",
            "participants": {
                 "person1": {
                    "place": "Berlin, Germany",
                    "year": 1985,
                    "month": 6,
                    "day": 15,
                    "hour": 14,
                    "minute": 30
                },
                 "person2": {
                    "place": "New York, USA",
                    "year": 1980,
                    "month": 2,
                    "day": 10,
                    "hour": 9,
                    "minute": 15
                },
                 "person3": {
                    "place": "London, UK",
                    "year": 1990,
                    "month": 12,
                    "day": 5,
                    "hour": 18,
                    "minute": 45
                }
            }
        }],
        description="Enhanced Penta Analysis v2 with Group Type configuration."
    ),
    authorized: bool = Depends(verify_token)
):
    """
    Enhanced Penta Analysis (v2) returns a semantic JSON structure with Channels, Gaps, and Functional Zones.
    """
    inputs = request.participants
    
    # Validation
    if len(inputs) < 3: 
        if len(inputs) < 3 or len(inputs) > 5:
             # Strict 3-5 as per "Penta" definition
             pass

    # Processing Loop
    participants_gates = {}
    
    for name, p_input in inputs.items():
        try:
            # Geocoding & Timezone
            if p_input.latitude is not None and p_input.longitude is not None:
                latitude, longitude = p_input.latitude, p_input.longitude
            else:
                latitude, longitude = get_latitude_longitude(p_input.place)
                
            if latitude is None or longitude is None:
                 raise HTTPException(status_code=400, detail=f"Geocoding failed for {name} place: '{p_input.place}'")
            
            if "/" in p_input.place:
                zone = p_input.place
            else:
                tf = TimezoneFinder()
                zone = tf.timezone_at(lat=latitude, lng=longitude) or 'Etc/UTC'
            
            birth_time = (p_input.year, p_input.month, p_input.day, p_input.hour, p_input.minute, 0)
            hours = hd.get_utc_offset_from_tz(birth_time, zone)
            timestamp = (p_input.year, p_input.month, p_input.day, p_input.hour, p_input.minute, 0, hours)
            
            # Calculate Gates
            temp_persons_dict = {name: timestamp}
            gates_dict = hd.get_single_hd_features(temp_persons_dict, name, 'date_to_gate_dict')
            participants_gates[name] = gates_dict
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing input for {name}: {str(e)}")

    # Call v2 Logic with Group Type
    try:
        result = hd.get_penta(participants_gates, group_type=request.group_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in Penta v2 calculation: {str(e)}")

    return result

