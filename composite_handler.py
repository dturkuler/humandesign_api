import hd_features as hd
import hd_constants
import pandas as pd
import numpy as np
from datetime import datetime
from geocode import get_latitude_longitude
from timezonefinder import TimezoneFinder
import pytz

def sanitize_for_json(data):
    """
    Recursively converts numpy types in a data structure to native Python types.
    Handles dicts, lists, tuples, and numpy scalars/arrays.
    """
    if isinstance(data, dict):
        return {k: sanitize_for_json(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_for_json(v) for v in data]
    elif isinstance(data, tuple):
        return tuple(sanitize_for_json(v) for v in data)
    elif isinstance(data, (np.integer, int)):
        return int(data)
    elif isinstance(data, (np.floating, float)):
        return float(data)
    elif isinstance(data, np.ndarray):
        return sanitize_for_json(data.tolist())
    else:
        return data

def process_person_data(name, data):
    """
    Process a single person's data: geocode, timezone, HD features.
    Returns (timestamp, person_details_dict).
    """
    try:
        place = data["place"]
        # Extract inputs (assuming standard keys or tuple-like access if needed, but dict is better)
        # We expect data to be a dict from the API model
        year = data["year"]
        month = data["month"]
        day = data["day"]
        hour = data["hour"]
        minute = data["minute"]
        
        # Geocode
        latitude, longitude = get_latitude_longitude(place)
        if latitude is None or longitude is None:
            raise ValueError(f"Could not geocode place: {place}")

        # Timezone
        tf = TimezoneFinder()
        zone = tf.timezone_at(lat=latitude, lng=longitude) or 'Etc/UTC'
        
        # Calculate UTC offset
        birth_time = (year, month, day, hour, minute, 0) # seconds default 0
        hours_offset = hd.get_utc_offset_from_tz(birth_time, zone)
        
        # HD Timestamp
        timestamp = (year, month, day, hour, minute, 0, int(hours_offset))
        
        # Calculate HD Features
        hd_data = hd.unpack_single_features(
            hd.calc_single_hd_features(timestamp, report=False, channel_meaning=True)
        )
        
        # Format Dates
        # Standardize birth_date to ISO UTC
        try:
             # Create timezone object
            local_tz = pytz.timezone(zone)
            local_dt = local_tz.localize(datetime(*birth_time))
            utc_dt = local_dt.astimezone(pytz.utc)
            formatted_birth_date = utc_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        except Exception:
             # Fallback
             formatted_birth_date = str(timestamp)


        formatted_create_date = "Unknown"
        try:
            c_date_str = hd_data["create_date"]
            c_date_parts = [int(p) for p in c_date_str.strip("()").split(",")]
            c_dt = datetime(*c_date_parts)
            formatted_create_date = c_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        except Exception:
             formatted_create_date = hd_data["create_date"]

        # Map HD Attributes
        energy_type = hd_constants.TYPE_DETAILS_MAP.get(hd_data["typ"], {}).get("type", hd_data["typ"])
        type_details = hd_constants.TYPE_DETAILS_MAP.get(hd_data["typ"], {})
        
        auth_code = hd_data["auth"]
        inner_authority = hd_constants.INNER_AUTHORITY_NAMES_MAP.get(auth_code, auth_code)
        
        # Centers
        defined_centers_names = [hd_constants.CHAKRA_NAMES_MAP.get(c, c) for c in hd_data["active_chakra"]]
        undefined_centers_names = [hd_constants.CHAKRA_NAMES_MAP.get(c, c) for c in (set(hd_constants.CHAKRA_LIST) - set(hd_data["active_chakra"]))]
        
        # Cross
        descriptive_inc_cross = str(hd_data["inc_cross"])
        try:
            date_to_gate = hd_data["date_to_gate_dict"]
            p_sun_gate = date_to_gate["gate"][0]
            inc_typ = hd_data["inc_cross_typ"]
            cross_info = hd_constants.CROSS_DB.get(p_sun_gate)
            if cross_info and inc_typ in cross_info:
                 descriptive_inc_cross = cross_info[inc_typ]
            else:
                 descriptive_inc_cross = f"{hd_data['inc_cross']}-{inc_typ}"
        except Exception:
             pass

        # Channels
        channels_list = []
        if "active_channel" in hd_data:
             ac = hd_data["active_channel"]
             gates = ac.get("ch_gate", [])
             meanings = ac.get("meaning", [])
             for i in range(len(gates) // 2): # Iterate by pairs? No, ch_gate is list of gates. 
                 # Wait, run_composite_combinations loop was: range(len(gates)) where gates is list of [g1, g2]
                 # Let's check format. 'active_channels' from unpack is dict.
                 # Actually calc_single_hd_features returns dict with keys 'ch_gate' which is list of [g1, g2] lists.
                 # Let's verify... yes.
                 pass
             
             # Re-structure properly
             ch_gates = ac.get("ch_gate", [])
             # meanings matches length of ch_gates
             for i, g_pair in enumerate(ch_gates):
                 ch_data = {"gates": g_pair}
                 if i < len(meanings):
                     ch_data["meaning"] = meanings[i]
                 channels_list.append(ch_data)


        # Profile
        profile_code = tuple(hd_data["profile"]) if isinstance(hd_data["profile"], list) else hd_data["profile"]
        profile_desc = hd_constants.PROFILE_DB.get(profile_code, f"{profile_code[0]}/{profile_code[1]}")

        person_details = {
            "name": name, # Echo name back
            "place": place,
            "tz": zone,
            "birth_date": formatted_birth_date,
            "create_date": formatted_create_date,
            "energy_type": energy_type,
            "strategy": type_details.get("strategy"),
            "signature": type_details.get("signature"),
            "not_self": type_details.get("not_self"),
            "aura": type_details.get("aura"),
            "inner_authority": inner_authority,
            "inc_cross": descriptive_inc_cross,
            "profile": profile_desc,
            "defined_centers": defined_centers_names,
            "undefined_centers": undefined_centers_names,
            "definition": hd_constants.DEFINITION_DB.get(str(hd_data["definition"]), str(hd_data["definition"])),
            "channels": channels_list
        }
        
        return timestamp, person_details

    except Exception as e:
        # Log error or re-raise
        print(f"Error processing person {name}: {e}")
        return None, None

def process_composite_matrix(persons_input):
    """
    Main handler for /compmatrix endpoint.
    persons_input: Dict[str, dict] where dict has keys: place, year, month, day, hour, minute
    """
    processed_persons_dict = {}
    utc_birthdata_dict = {}
    
    # 1. Process Individuals
    for name, data in persons_input.items():
        # Ensure data is dict-like
        if hasattr(data, "dict"):
             data = data.dict()
             
        ts, details = process_person_data(name, data)
        if ts:
            processed_persons_dict[name] = ts
            utc_birthdata_dict[name] = details
            
    if len(processed_persons_dict) < 2:
        # Not a matrix if less than 2, but we can still return person details
        pass

    # 2. Calculate Combinations (if enough people)
    combinations_list = []
    if len(processed_persons_dict) >= 2:
        result_df = hd.get_composite_combinations(processed_persons_dict)
        # Convert to list of dicts
        combinations_list = result_df.to_dict(orient="records")
        
        # 3. Enrich Combinations (Map Charkas)
        for combo in combinations_list:
            if "new_chakra" in combo and isinstance(combo["new_chakra"], list):
                combo["new_chakra"] = [hd_constants.CHAKRA_NAMES_MAP.get(c, c) for c in combo["new_chakra"]]

    # 4. Construct Output
    output_data = {
        "persons": utc_birthdata_dict,
        "combinations": combinations_list
    }
    
    # 5. Sanitize for JSON (Numpy types)
    final_output = sanitize_for_json(output_data)
    
    return final_output
