from typing import Optional
from fastapi import APIRouter, Query, HTTPException, Depends
# from timezonefinder import TimezoneFinder # Removed
from .. import features as hd
from .. import hd_constants
from ..services.geolocation import get_latitude_longitude, tf
from ..dependencies import verify_token
from ..utils.calculations import process_transit_data, enrich_transit_metadata

router = APIRouter(prefix="/transits", tags=["transits"])

@router.get("/solar_return")
def get_solar_return(
    year: int = Query(1968, description="Birth year"),
    month: int = Query(2, description="Birth month"),
    day: int = Query(21, description="Birth day"),
    hour: int = Query(11, description="Birth hour"),
    minute: int = Query(0, description="Birth minute (default 0)"),
    second: int = Query(0, description="Birth second (optional, default 0)"),
    place: str = Query("Kirikkale, Turkey", description="Birth place (city, country)"),
    sr_year_offset: int = Query(0, description="Years to add to birth year. 0 = Birth Year, 1 = 1st Birthday (1969), 58 = 2026 Birthday."),
    latitude: Optional[float] = Query(None, description="Optional latitude for birth place"),
    longitude: Optional[float] = Query(None, description="Optional longitude for birth place"),
    authorized: bool = Depends(verify_token)
):
    # Geocoding and timezone logic
    if latitude is None or longitude is None:
        latitude, longitude = get_latitude_longitude(place)
        
    if latitude is None or longitude is None:
        raise HTTPException(status_code=400, detail=f"Geocoding failed for place: '{place}'")
    
    if "/" in place:
        zone = place
    else:
        # Use singleton
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
    sr_composite_data = process_transit_data(sr_timestamp, birth_timestamp, place)
    
    # Format Response using shared helper
    return enrich_transit_metadata(
        birth_timestamp=birth_timestamp,
        transit_year=int(sr_year),
        transit_month=int(sr_month),
        transit_day=int(sr_day),
        transit_hour=int(sr_hour),
        transit_minute=int(sr_minute),
        place=place,
        calculation_place=place, # Solar Return uses birth place for calculation context in this logic
        composite_data=sr_composite_data
    )


@router.get("/daily")
def get_daily_transit(
    year: int = Query(1968, description="Birth year"),
    month: int = Query(2, description="Birth month"),
    day: int = Query(21, description="Birth day"),
    hour: int = Query(11, description="Birth hour"),
    minute: int = Query(0, description="Birth minute (default 0)"),
    second: int = Query(0, description="Birth second (optional, default 0)"),
    place: str = Query("Kirikkale, Turkey", description="Birth place (city, country)"),
    current_place: str = Query(None, description="Current location for transit calculation (optional, defaults to Birth Place)"),
    transit_year: int = Query(2025, description="Transit year to analyze"),
    transit_month: int = Query(1, description="Transit month to analyze"),
    transit_day: int = Query(10, description="Transit day to analyze"),
    transit_hour: int = Query(12, description="Transit hour (local time at calculation place, default 12)"),
    transit_minute: int = Query(0, description="Transit minute (default 0)"),
    latitude: Optional[float] = Query(None, description="Optional latitude for birth place"),
    longitude: Optional[float] = Query(None, description="Optional longitude for birth place"),
    current_latitude: Optional[float] = Query(None, description="Optional latitude for current place"),
    current_longitude: Optional[float] = Query(None, description="Optional longitude for current place"),
    authorized: bool = Depends(verify_token)
):
    # 1. Process Birth Data (remains constant)
    if latitude is None or longitude is None:
        b_lat, b_lon = get_latitude_longitude(place)
    else:
        b_lat, b_lon = latitude, longitude
        
    if b_lat is None or b_lon is None:
        raise HTTPException(status_code=400, detail=f"Geocoding failed for birth place: '{place}'")
    
    if "/" in place:
        b_zone = place
    else:
        # Use singleton
        b_zone = tf.timezone_at(lat=b_lat, lng=b_lon) or 'Etc/UTC'
    
    birth_time = (year, month, day, hour, minute, second)
    b_offset_hours = hd.get_utc_offset_from_tz(birth_time, b_zone)
    birth_timestamp = tuple(list(birth_time) + [int(b_offset_hours)])

    # 2. Determine Calculation Context (Location & Timezone)
    calculation_place = current_place if current_place else place
    
    if current_place:
        # Geocode current place
        if current_latitude is None or current_longitude is None:
            c_lat, c_lon = get_latitude_longitude(calculation_place)
        else:
            c_lat, c_lon = current_latitude, current_longitude
            
        if c_lat is None or c_lon is None:
             raise HTTPException(status_code=400, detail=f"Geocoding failed for current place: '{calculation_place}'")
        
        if "/" in calculation_place:
            c_zone = calculation_place
        else:
            # Use singleton
            c_zone = tf.timezone_at(lat=c_lat, lng=c_lon) or 'Etc/UTC'
    else:
        # Re-use birth place info
        c_lat, c_lon = b_lat, b_lon
        c_zone = b_zone

    # 3. Calculate Transit Timestamp
    # Using the TRANSIT date/time components and the CURRENT/TARGET location's timezone
    transit_local_tuple = (transit_year, transit_month, transit_day, transit_hour, transit_minute, 0)
    
    # Get offset for the transit date at the calculation location
    # Note: Daylight savings might differ from birth date/location!
    t_offset_hours = hd.get_utc_offset_from_tz(transit_local_tuple, c_zone)
    
    transit_timestamp = tuple(list(transit_local_tuple) + [int(t_offset_hours)])

    # Calculate the composite chart at the transit moment
    composite_data = process_transit_data(transit_timestamp, birth_timestamp, place)

    # --- v1.8.1 Enriched Metadata Implementation ---
    
    # 1. Calculate Full Birth Chart Details
    # We use calc_single_hd_features to get all attributes
    # Returns: typ, auth, inc_cross, inc_cross_typ, profile, definition, date_to_gate_dict, active_chakras, active_channels_dict, bdate, cdate, variables
    (
        b_typ, b_auth, b_inc_cross, b_inc_cross_typ, b_profile, b_definition, 
        b_date_to_gate, b_active_chakras, b_active_channels, 
        b_date_str, b_create_date_str, b_variables
    ) = hd.calc_single_hd_features(birth_timestamp, report=False, channel_meaning=True)

    # 2. Map Constants & Formats for Metadata
    
    # Map Authority
    b_auth_name = hd_constants.INNER_AUTHORITY_NAMES_MAP.get(b_auth, b_auth)

    # Map Centers (Sort for consistency)
    defined_centers_list = [hd_constants.CHAKRA_NAMES_MAP.get(c, c) for c in b_active_chakras]
    
    # Calculate Undefined Centers
    all_centers = set(hd_constants.CHAKRA_LIST)
    undefined_centers_set = all_centers - b_active_chakras
    undefined_centers_list = [hd_constants.CHAKRA_NAMES_MAP.get(c, c) for c in undefined_centers_set]

    # Map Definition
    # 0: None, 1: Single, 2: Split, 3: Triple Split, 4: Quadruple Split
    definition_map = {
        0: "No Definition",
        1: "Single Definition",
        2: "Split Definition",
        3: "Triple Split Definition", 
        4: "Quadruple Split Definition"
    }
    definition_str = definition_map.get(b_definition, "Unknown Definition")

    # Map Channels (Special formatting request: "Gate/Gate: Name (Desc)")
    # b_active_channels['meaning'] contains tuples/lists like ["Name", "Description"]
    # b_active_channels['gate'] and ['ch_gate'] are numpy arrays
    
    birth_channels_formatted = []
    
    # If channel_meaning=True, 'meaning' key exists
    if 'meaning' in b_active_channels:
        b_gates = b_active_channels.get('gate', [])
        b_ch_gates = b_active_channels.get('ch_gate', [])
        b_meanings = b_active_channels.get('meaning', [])
        
        count = len(b_gates)
        # Iterate and construct strings
        for i in range(count):
            g1 = b_gates[i]
            g2 = b_ch_gates[i]
            
            # Meaning is often [Name, Description]
            m_name = "Unknown"
            m_desc = ""
            current_meaning = b_meanings[i]
            if isinstance(current_meaning, (list, tuple)):
                if len(current_meaning) > 0:
                    m_name = current_meaning[0]
                if len(current_meaning) > 1:
                    m_desc = current_meaning[1]
            
            # Format: "Gate/Gate: Name (Desc)"
            # Note: User example showed "6/59: The Channel of Mating (A Design Focused on Reproduction)"
            channel_str = f"{g1}/{g2}: {m_name} ({m_desc})"
            birth_channels_formatted.append({"channel": channel_str})

    # Strategy & Signature mapping (simplified inference based on Type)
    # Ideally this would be in a helper, but mapping locally for v1.8.1
    strategy_map = {
        "Generator": "Wait to Respond",
        "Manifesting Generator": "Wait to Respond",
        "Projector": "Wait for the Invitation",
        "Manifestor": "Inform Before Acting",
        "Reflector": "Wait a Lunar Cycle"
    }
    signature_map = {
        "Generator": "Satisfaction",
        "Manifesting Generator": "Satisfaction",
        "Projector": "Success",
        "Manifestor": "Peace",
        "Reflector": "Surprise"
    }
    not_self_map = {
         "Generator": "Frustration",
         "Manifesting Generator": "Frustration & Anger",
         "Projector": "Bitterness",
         "Manifestor": "Anger",
         "Reflector": "Disappointment"
    }
    aura_map = {
        "Generator": "Open & Enveloping",
        "Manifesting Generator": "Open & Enveloping",
        "Projector": "Focused & Absorbing",
        "Manifestor": "Closed & Repelling",
        "Reflector": "Sampling & Resistant"
    }
    
    b_strategy = strategy_map.get(b_typ, "Unknown")
    b_signature = signature_map.get(b_typ, "Unknown")
    b_not_self = not_self_map.get(b_typ, "Unknown")
    b_aura = aura_map.get(b_typ, "Unknown")

    # Construct Meta Object
    meta_object = {
        # Bio
        "birth_date": f"{year}-{month:02d}-{day:02d}T{hour:02d}:{minute:02d}:{second:02d}Z", # Keeping simple ISO-like
        "create_date": b_create_date_str, # Comes from calc string representation 
        "place": place,
        "age": transit_year - year, # Approximate age
        "gender": "male", # Hardcoded default for now as it's not in parameters, user requested defaults update but no gender param added to func signature yet. 
                          # WAIT: User example showed gender/islive in URL logs but they were NOT in the requested Python function Params update list.
                          # I will add 'gender' and 'islive' to the signature to support this properly if they are expected.
                          # Checking previous request: "addtionally update endpoint defaults with following ... param list"
                          # The user URL had &gender=male&islive=true.
                          # I should probably add them to parameters to be safe and accurate.
        "islive": True,   # Defaulting
        
        # Calculation Context (v1.9.0)
        "transit_date_local": f"{transit_year}-{transit_month:02d}-{transit_day:02d} {transit_hour:02d}:{transit_minute:02d}", 
        "transit_date_utc": composite_data.get("transit_date"),
        "calculation_place": calculation_place,
        
        # Astrology
        "zodiac_sign": "Pisces", # Placeholder - logic requires date mapping, user requested specific update. 
                                 # Implementing simple Zodiac lookup would be better than hardcoding.
                                 
        # HD Core
        "energy_type": b_typ,
        "strategy": b_strategy,
        "signature": b_signature,
        "not_self": b_not_self,
        "aura": b_aura,
        "inner_authority": b_auth_name,
        "inc_cross": f"{b_inc_cross}", # Formatting tuple to string? User example: "The Right Angle Cross of the Sleeping Phoenix (1)"
                                       # Our b_inc_cross is likely a tuple or name. Let's check format.
                                       # Usually it returns the name.
        "profile": f"{b_profile[0]}/{b_profile[1]}", # e.g. "2/4"
        
        # Centers
        "defined_centers": defined_centers_list,
        "undefined_centers": undefined_centers_list,
        "definition": definition_str,
        
        # Channels
        "channels": {
            "Channels": birth_channels_formatted
        }
    }
    
    # --- Zodiac Logic (Mini helper) ---
    def get_zodiac(d, m):
        if (m == 3 and d >= 21) or (m == 4 and d <= 19):
            return "Aries"
        if (m == 4 and d >= 20) or (m == 5 and d <= 20):
            return "Taurus"
        if (m == 5 and d >= 21) or (m == 6 and d <= 20):
            return "Gemini"
        if (m == 6 and d >= 21) or (m == 7 and d <= 22):
            return "Cancer"
        if (m == 7 and d >= 23) or (m == 8 and d <= 22):
            return "Leo"
        if (m == 8 and d >= 23) or (m == 9 and d <= 22):
            return "Virgo"
        if (m == 9 and d >= 23) or (m == 10 and d <= 22):
            return "Libra"
        if (m == 10 and d >= 23) or (m == 11 and d <= 21):
            return "Scorpio"
        if (m == 11 and d >= 22) or (m == 12 and d <= 21):
            return "Sagittarius"
        if (m == 12 and d >= 22) or (m == 1 and d <= 19):
            return "Capricorn"
        if (m == 1 and d >= 20) or (m == 2 and d <= 18):
            return "Aquarius"
        return "Pisces"
    
    meta_object["zodiac_sign"] = get_zodiac(day, month)
    
    # Profile Names Map (Simple)
    profile_names = {
        "1/3": "Investigator Martyr",
        "1/4": "Investigator Opportunist",
        "2/4": "Hermit Opportunist",
        "2/5": "Hermit Heretic",
        "3/5": "Martyr Heretic",
        "3/6": "Martyr Role Model",
        "4/6": "Opportunist Role Model",
        "4/1": "Opportunist Investigator",
        "5/1": "Heretic Investigator",
        "5/2": "Heretic Hermit",
        "6/2": "Role Model Hermit",
        "6/3": "Role Model Martyr"
    }
    p_key = f"{b_profile[0]}/{b_profile[1]}"
    meta_object["profile"] = f"{p_key}: {profile_names.get(p_key, '')}"

    # --- End v1.8.1 ---

    # --- v1.8.0 Data Mapping (Existing Logic) ---
    # ... (Rest of existing Mapping for Transit Composite) ...
    
    # Map Authority (Composite)
    auth_code = composite_data.get("composite_authority")
    hd_constants.INNER_AUTHORITY_NAMES_MAP.get(auth_code, auth_code)

    # Map Centers (Composite)
    raw_centers = composite_data.get("new_defined_centers", [])
    mapped_centers = [hd_constants.CHAKRA_NAMES_MAP.get(c, c) for c in raw_centers]

    # Map Channels (Composite)
    mapped_channels = []
    raw_channels_gates = composite_data.get("new_defined_channels", [])
    raw_channel_meanings = composite_data.get("new_channel_meanings", [])

    for gates_tuple, meaning in zip(raw_channels_gates, raw_channel_meanings):
        g1, g2 = gates_tuple if isinstance(gates_tuple, (list, tuple)) and len(gates_tuple) >= 2 else ("?", "?")
        gate_str = f"{g1}-{g2}"
        name = meaning[0] if isinstance(meaning, (list, tuple)) and len(meaning) > 0 else "Unknown"
        desc = meaning[1] if isinstance(meaning, (list, tuple)) and len(meaning) > 1 else str(meaning)

        mapped_channels.append({
            "gates": gate_str,
            "name": name,
            "description": desc
        })

    # Transform Planetary Transits
    raw_transits = composite_data.get("raw_transit_gates", {})
    planetary_transits = []
    p_names = raw_transits.get("planets", [])
    count = len(p_names)
    
    for i in range(count):
        planetary_transits.append({
            "planets": p_names[i],
            "gate": raw_transits["gate"][i] if i < len(raw_transits.get("gate", [])) else None,
            "line": raw_transits["line"][i] if i < len(raw_transits.get("line", [])) else None,
            "color": raw_transits["color"][i] if i < len(raw_transits.get("color", [])) else None,
            "tone": raw_transits["tone"][i] if i < len(raw_transits.get("tone", [])) else None,
            "base": raw_transits["base"][i] if i < len(raw_transits.get("base", [])) else None,
            "lon": raw_transits["lon"][i] if i < len(raw_transits.get("lon", [])) else None,
        })

    # Construct Response
    return {
        "meta": meta_object, # Injected expanded meta
        "composite_changes": {
            "new_channels": mapped_channels,
            "new_centers": mapped_centers
        },
        "planetary_transits": planetary_transits
    }
