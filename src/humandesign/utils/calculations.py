from .. import features as hd
from .. import hd_constants
from .date_utils import to_iso_utc, clean_birth_date_to_iso

# --- Helper to process transit data ---
def process_transit_data(transit_date_timestamp, birth_timestamp, birth_place):
    # 1. Calculate birth chart to get natal features (prs + des)
    birth_features = hd.calc_single_hd_features(birth_timestamp, report=False, channel_meaning=True, day_chart_only=False)
    natal_gate_dict = birth_features[6]

    # 2. Calculate day chart (transit features only)
    day_gate_dict = hd.calc_single_hd_features(transit_date_timestamp, day_chart_only=True)
    # Round longitude to 3 decimal places for clean output
    if 'lon' in day_gate_dict:
        day_gate_dict['lon'] = [round(x, 3) for x in day_gate_dict['lon']]
    
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
    # Refactored to avoid using hd.composite_chakras_channels which incorrectly 
    # calculates the full chart (Personality + Design) for the transit timestamp.
    # We only want to compare Composite (Natal + Transit Personality) vs Natal.
    
    # Natal features from Step 1
    # birth_features structure:
    # 0:typ, 1:auth, 2:inc_cross, 3:inc_cross_typ, 4:profile, 5:definition, 
    # 6:date_to_gate_dict, 7:active_chakras, 8:active_channels_dict
    natal_active_chakras = set(birth_features[7])
    natal_active_channels_dict = birth_features[8]

    # Calculate New Centers
    # active_chakras is the Composite set (from Step 4)
    new_centers_list = list(set(active_chakras) - natal_active_chakras)
    
    # Calculate New Channels
    # We compare the 'meaning' list (tuples of Name, Desc) or formatted strings.
    # active_channels_dict is Composite.
    
    new_channels_data = {
        "gate": [],
        "ch_gate": [],
        "meaning": []
    }
    
    # Helper to create a unique key for channels (sorted tuple of gates)
    def ch_key(g1, g2):
        return tuple(sorted((g1, g2)))

    # Get Natal Channel Keys
    natal_keys = set()
    if 'gate' in natal_active_channels_dict:
        n_gates = natal_active_channels_dict['gate']
        n_ch_gates = natal_active_channels_dict['ch_gate']
        count_n = len(n_gates)
        for i in range(count_n):
            natal_keys.add(ch_key(n_gates[i], n_ch_gates[i]))

    # Iterate Composite Channels and find new ones
    if 'gate' in active_channels_dict:
        c_gates = active_channels_dict['gate']
        c_ch_gates = active_channels_dict['ch_gate']
        c_meanings = active_channels_dict.get('meaning', [])
        
        count_c = len(c_gates)
        for i in range(count_c):
            g1 = c_gates[i]
            g2 = c_ch_gates[i]
            k = ch_key(g1, g2)
            
            if k not in natal_keys:
                # It's new!
                new_channels_data["gate"].append(g1)
                new_channels_data["ch_gate"].append(g2)
                # Handle meaning safely
                m = c_meanings[i] if i < len(c_meanings) else ("Unknown", "")
                new_channels_data["meaning"].append(m)

    # offset for birth date
    birth_offset = birth_timestamp[6] 
    
    # 6. Structure output
    raw_output = {
        "transit_date": to_iso_utc(transit_date_timestamp),
        "birth_date": clean_birth_date_to_iso(birth_features[9], birth_offset),
        "birth_place": birth_place,
        "composite_type": typ,
        "composite_authority": auth,
        "new_defined_channels": list(zip(new_channels_data["gate"], new_channels_data["ch_gate"])),
        "new_channel_meanings": new_channels_data["meaning"],
        "new_defined_centers": new_centers_list,
        "total_defined_centers": len(active_chakras),
        "raw_transit_gates": day_gate_dict
    }
    
    return sanitize_to_native(raw_output)

def sanitize_to_native(obj):
    """
    Recursively convert numpy types to native Python types.
    """
    import numpy as np
    
    if isinstance(obj, dict):
        return {k: sanitize_to_native(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [sanitize_to_native(i) for i in obj]
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return sanitize_to_native(obj.tolist())
    else:
        return obj

def enrich_transit_metadata(
    birth_timestamp, 
    transit_year, 
    transit_month, 
    transit_day, 
    transit_hour, 
    transit_minute,
    place,
    calculation_place,
    composite_data
):
    """
    Enriches the transit response with full birth chart metadata and standardized structure.
    Returns the final dictionary ready for sanitization.
    """
    
    # 1. Calculate Full Birth Chart Details
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
    definition_map = {
        0: "No Definition",
        1: "Single Definition",
        2: "Split Definition",
        3: "Triple Split Definition", 
        4: "Quadruple Split Definition"
    }
    definition_str = definition_map.get(b_definition, "Unknown Definition")

    # Map Channels
    birth_channels_formatted = []
    
    if 'meaning' in b_active_channels:
        b_gates = b_active_channels.get('gate', [])
        b_ch_gates = b_active_channels.get('ch_gate', [])
        b_meanings = b_active_channels.get('meaning', [])
        
        count = len(b_gates)
        for i in range(count):
            g1 = b_gates[i]
            g2 = b_ch_gates[i]
            
            m_name = "Unknown"
            m_desc = ""
            current_meaning = b_meanings[i]
            if isinstance(current_meaning, (list, tuple)):
                if len(current_meaning) > 0:
                    m_name = current_meaning[0]
                if len(current_meaning) > 1:
                    m_desc = current_meaning[1]
            
            channel_str = f"{g1}/{g2}: {m_name} ({m_desc})"
            birth_channels_formatted.append({"channel": channel_str})

    # Strategy & Signature mapping
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
    # Extract Birth Date/Time from timestamp (tuple) or passed args?
    # birth_timestamp is (y, m, d, h, m, s, offset)
    # We can reconstruct ISO from it loosely or use b_date_str from HD calc?
    # HD calc returns b_date_str, let's use what we have or just format inputs if passed.
    # The caller passes birth_timestamp, let's use that.
    
    meta_object = {
        # Bio
        "birth_date": f"{birth_timestamp[0]}-{birth_timestamp[1]:02d}-{birth_timestamp[2]:02d}T{birth_timestamp[3]:02d}:{birth_timestamp[4]:02d}:{birth_timestamp[5]:02d}Z",
        "create_date": b_create_date_str,
        "place": place,
        "age": transit_year - birth_timestamp[0], 
        "gender": "male", # Keeping hardcoded default as per v1.8.1 parity
        "islive": True,
        
        # Calculation Context
        "transit_date_local": f"{transit_year}-{transit_month:02d}-{transit_day:02d} {transit_hour:02d}:{transit_minute:02d}", 
        "transit_date_utc": composite_data.get("transit_date"),
        "calculation_place": calculation_place,
        
        # Astrology
        "zodiac_sign": "Pisces", # Placeholder - will run helper
                                 
        # HD Core
        "energy_type": b_typ,
        "strategy": b_strategy,
        "signature": b_signature,
        "not_self": b_not_self,
        "aura": b_aura,
        "inner_authority": b_auth_name,
        "inc_cross": f"{b_inc_cross}",
        "profile": f"{b_profile[0]}/{b_profile[1]}",
        
        # Centers
        "defined_centers": defined_centers_list,
        "undefined_centers": undefined_centers_list,
        "definition": definition_str,
        
        # Channels
        "channels": {
            "Channels": birth_channels_formatted
        }
    }
    
    # Zodiac Logic
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
    
    meta_object["zodiac_sign"] = get_zodiac(birth_timestamp[2], birth_timestamp[1])
    
    # Profile Names Map
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

    # Map Composite Data
    composite_data.get("composite_authority")
    # auth_name = hd_constants.INNER_AUTHORITY_NAMES_MAP.get(auth_code, auth_code) # Not used in output structure of daily? 
    # Wait, daily output has composite_changes and planetary_transits seperately.
    
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

    return {
        "meta": meta_object,
        "composite_changes": {
            "new_channels": mapped_channels,
            "new_centers": mapped_centers
        },
        "planetary_transits": planetary_transits
    }
