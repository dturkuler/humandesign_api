from .. import features as hd
from .. import hd_constants
import pandas as pd
import numpy as np
from datetime import datetime
from .geolocation import get_latitude_longitude
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

def classify_maia_connection(p1_gates, p2_gates, channel):
    """
    Classifies the connection type for a single channel between two people.
    channel: tuple(gate1, gate2)
    """
    g1, g2 = channel
    p1_has_g1 = g1 in p1_gates
    p1_has_g2 = g2 in p1_gates
    p2_has_g1 = g1 in p2_gates
    p2_has_g2 = g2 in p2_gates
    
    p1_full = p1_has_g1 and p1_has_g2
    p2_full = p2_has_g1 and p2_has_g2
    
    if p1_full and p2_full:
        return "Companionship"
    
    if p1_full:
        if p2_has_g1 or p2_has_g2:
            return "Compromise"
        return "Dominance"
        
    if p2_full:
        if p1_has_g1 or p1_has_g2:
            return "Compromise"
        return "Dominance"
    
    # If neither is full, must be electromagnetic (or nothing, but caller ensures it's a connection)
    return "Electromagnetic"

def get_connection_classification(defined_centers_count):
    """
    Returns the '9-0' style code and professional theme.
    """
    mapping = {
        9: "9-0 Nowhere to go",
        8: "8-1 Have some fun",
        7: "7-2 Work to do",
        6: "6-3 Better to be free",
        5: "5-4 Not a door"
    }
    return mapping.get(defined_centers_count, f"{defined_centers_count}-{9-defined_centers_count}")

def calculate_center_dynamics(p1_centers, p2_centers):
    """
    Determines who is conditioning whom for each center.
    Returns a dict {CenterName: DynamicType}
    """
    dynamics = {}
    for code, name in hd_constants.CHAKRA_NAMES_MAP.items():
        p1_fixed = name in p1_centers
        p2_fixed = name in p2_centers
        
        if p1_fixed and p2_fixed:
            dynamics[name] = "fixed"
        elif p1_fixed:
            dynamics[name] = "conditioning_p1_to_p2"
        elif p2_fixed:
            dynamics[name] = "conditioning_p2_to_p1"
        else:
            dynamics[name] = "open_window"
    return dynamics

def check_bridging(p_defined, combo_defined):
    """
    Checks if the composite bridges a split definition.
    Simple heuristic: if person has >1 island and composite has 1 island.
    """
    # Note: Definition codes are strings like '1', '2', '3'
    # 1=Single, 2=Split, 3=Triple, 4=Quad
    try:
        if int(p_defined) > 1 and int(combo_defined) == 1:
            return True
    except:
        pass
    return False

def get_aura_dynamic(type1, type2):
    """
    Returns professional Maian labels for Aura interactions.
    """
    pair = sorted([(type1 or "Unknown"), (type2 or "Unknown")])
    dynamics = {
        ("Generator", "Generator"): "Shared Responding Cycle",
        ("Generator", "Manifesting Generator"): "Mixed Build-Through Cycle",
        ("Generator", "Projector"): "Recognition & Energetic Guidance",
        ("Generator", "Manifestor"): "Request & Inform Dynamic",
        ("Generator", "Reflector"): "Sustainability & Sampling",
        ("Manifesting Generator", "Manifesting Generator"): "High-Velocity Build-Through",
        ("Manifesting Generator", "Projector"): "Speed & Energetic Efficiency",
        ("Manifesting Generator", "Manifestor"): "Initiating Velocity",
        ("Manifesting Generator", "Reflector"): "Power & Reflection",
        ("Projector", "Projector"): "Mutual Guidance & Success",
        ("Projector", "Manifestor"): "Strategy & Impact",
        ("Projector", "Reflector"): "Guidance & Sampling",
        ("Manifestor", "Manifestor"): "Impact & Mutual Informing",
        ("Manifestor", "Reflector"): "Inform & Reflect Dynamic",
        ("Reflector", "Reflector"): "Sampling & Lunar Harmony"
    }
    return dynamics.get(tuple(pair), "Neutral Energetic Dynamic")

def get_profile_resonance(p1_profile_str, p2_profile_str):
    """
    Determines resonance/harmony between two profiles.
    Resonant: Same profile.
    Harmonic: Lines match 1-4, 2-5, 3-6.
    """
    try:
        # Extract lines e.g. "1/3" -> [1, 3]
        p1_lines = [int(x) for x in p1_profile_str.split(":")[0].split("/")]
        p2_lines = [int(x) for x in p2_profile_str.split(":")[0].split("/")]
        
        if p1_lines == p2_lines:
            return "Profile Resonance (Identity)"
        
        harmonic_pairs = {(1, 4), (4, 1), (2, 5), (5, 2), (3, 6), (6, 3)}
        
        resonance_count = 0
        for l1 in p1_lines:
            for l2 in p2_lines:
                if (l1, l2) in harmonic_pairs:
                    resonance_count += 1
        
        if resonance_count >= 2:
            return "Deeply Harmonic (Profile Glue)"
        elif resonance_count == 1:
            return "Harmonic Resonance"
            
    except:
        pass
    return "Neutral Partnership"

def get_node_resonance(p1_nodes, p2_nodes):
    """
    Calculates Nodal Environmental resonance.
    p1_nodes, p2_nodes = set of gates for North/South nodes.
    """
    try:
        common = p1_nodes.intersection(p2_nodes)
        if common:
            return f"Shared Environment ({len(common)} Node Resonance)"
    except:
        pass
    return "Individual Environmental Paths"

def get_sub_circuit_detail(channel):
    """
    Returns granular sub-circuitry detail from hd_constants.
    """
    key = tuple(sorted(channel))
    sub = hd_constants.circuit_typ_dict.get(key, "Unknown")
    mapping = {
        "Knowledge": "Individual (Knowing)",
        "Centre": "Individual (Centering)",
        "Realize": "Collective (Logical)",
        "Sense": "Collective (Abstract/Sensing)",
        "Ego": "Tribal (Ego)",
        "Protect": "Tribal (Defense)",
        "Integration": "Integration"
    }
    return mapping.get(sub, sub)

def get_penta_dynamics(person_gates_dict):
    """
    Identifies functional gaps in a Penta (Group of 3-5).
    Maps to BUSINESS_SHADOW_MAP and BUSINESS_SKILLS_MAP in constants.
    """
    penta_gates = hd_constants.PENTA_GATES
    combined_gates = set()
    for gs in person_gates_dict.values():
        combined_gates.update(gs)
    
    skills = []
    shadows = []
    for g in penta_gates:
        if g in combined_gates:
            skills.append(hd_constants.BUSINESS_SKILLS_MAP.get(g, f"Gate {g}"))
        else:
            shadows.append(hd_constants.BUSINESS_SHADOW_MAP.get(g, f"Gate {g}"))
            
    return {
        "active_skills": skills,
        "penta_gaps": shadows,
        "is_functional": len(shadows) == 0
    }

def get_lunar_phase_flag(jd):
    """
    Calculates lunar context for Reflector-heavy or high-sensitivity interpretation.
    """
    try:
        res = swe.calc_ut(jd, swe.MOON)[0][0] # longitude
        sun_res = swe.calc_ut(jd, swe.SUN)[0][0]
        diff = (res - sun_res) % 360
        if diff < 45: return "New Moon Phase (Initiation)"
        if diff < 90: return "Waxing Crescent"
        if diff < 135: return "First Quarter (Action)"
        if diff < 180: return "Waxing Gibbous"
        if diff < 225: return "Full Moon (Clarity)"
        if diff < 270: return "Waning Gibbous"
        if diff < 315: return "Third Quarter (Release)"
    except:
        pass
    return "Neutral Lunar Cycle"

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
        if "/" in place:
            zone = place
        else:
            tf = TimezoneFinder()
            zone = tf.timezone_at(lat=latitude, lng=longitude) or 'Etc/UTC'
        
        # Calculate UTC offset
        birth_time = (year, month, day, hour, minute, 0) # seconds default 0
        hours_offset = hd.get_utc_offset_from_tz(birth_time, zone)
        
        # HD Timestamp
        timestamp = (year, month, day, hour, minute, 0, int(hours_offset))
        
        # Julian Day for Lunar Context
        # (Using a simple conversion or importing Julian utility if preferred, 
        # but we can reuse hd_features logic if we instantiate it)
        temp_instance = hd.hd_features(*timestamp)
        jd = temp_instance.timestamp_to_juldate(timestamp)
        lunar_phase = get_lunar_phase_flag(jd)

        # Calculate HD Features
        hd_rawData = hd.calc_single_hd_features(timestamp, report=False, channel_meaning=True)
        hd_data = hd.unpack_single_features(hd_rawData)
        
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
             gates_a = ac.get("gate", [])
             gates_b = ac.get("ch_gate", [])
             meanings = ac.get("meaning", [])
             
             for i in range(len(gates_a)):
                 ch_data = {"gates": [int(gates_a[i]), int(gates_b[i])]}
                 if i < len(meanings):
                     ch_data["meaning"] = meanings[i]
                 channels_list.append(ch_data)


        # Profile
        profile_code = tuple(hd_data["profile"]) if isinstance(hd_data["profile"], list) else hd_data["profile"]
        profile_desc = hd_constants.PROFILE_DB.get(profile_code, f"{profile_code[0]}/{profile_code[1]}")

        # Activation Matrix (High-Fidelity)
        activations_matrix = {}
        target_dict = hd_data["date_to_gate_dict"]
        for i in range(len(target_dict["gate"])):
            p_name = target_dict["planets"][i]
            activations_matrix[p_name] = {
                "gate": int(target_dict["gate"][i]),
                "line": int(target_dict["line"][i]),
                "color": int(target_dict["color"][i]),
                "tone": int(target_dict["tone"][i]),
                "base": int(target_dict["base"][i]),
                "planet": p_name
            }

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
            "variables": hd_data.get("variables"),
            "lunar_context": lunar_phase,
            "activations": activations_matrix,
            "channels": channels_list
        }
        
        return timestamp, person_details

    except Exception as e:
        # Log error or re-raise
        print(f"Error processing person {name}: {e}")
        return None, None

def process_composite_matrix(persons_input):
    """
    Main handler for /compmatrix endpoint. (Traditional)
    """
    processed_persons_dict = {}
    utc_birthdata_dict = {}
    
    for name, data in persons_input.items():
        if hasattr(data, "dict"): data = data.dict()
        ts, details = process_person_data(name, data)
        if ts:
            processed_persons_dict[name] = ts
            utc_birthdata_dict[name] = details
            
    combinations_list = []
    if len(processed_persons_dict) >= 2:
        result_df = hd.get_composite_combinations(processed_persons_dict)
        combinations_list = result_df.to_dict(orient="records")
        for combo in combinations_list:
            if "new_chakra" in combo and isinstance(combo["new_chakra"], list):
                combo["new_chakra"] = [hd_constants.CHAKRA_NAMES_MAP.get(c, c) for c in combo["new_chakra"]]

    return sanitize_for_json({"persons": utc_birthdata_dict, "combinations": combinations_list})

def process_maia_matrix(persons_input):
    """
    New handler for /maiamatrix endpoint. (Professional Maia Mechanics)
    """
    processed_persons_dict = {}
    utc_birthdata_dict = {}
    person_gates_map = {}
    person_gate_planet_map = {} # gate -> List[planet_name]
    person_nodes_map = {} # set of node gates
    person_definition_map = {}
    
    for name, data in persons_input.items():
        if hasattr(data, "dict"): data = data.dict()
        ts, details = process_person_data(name, data)
        if ts:
            processed_persons_dict[name] = ts
            utc_birthdata_dict[name] = details
            hd_rawData = hd.calc_single_hd_features(ts, report=False, channel_meaning=True)
            hd_unpacked = hd.unpack_single_features(hd_rawData)
            
            gates = set(hd_unpacked["date_to_gate_dict"]["gate"])
            person_gates_map[name] = gates
            person_definition_map[name] = hd_unpacked["definition"]
            
            # Extract planet triggers
            gate_to_planet = {}
            nodes = set()
            raw_gates = hd_unpacked["date_to_gate_dict"]["gate"]
            raw_planets = hd_unpacked["date_to_gate_dict"]["planets"]
            for i in range(len(raw_gates)):
                g = int(raw_gates[i])
                p_name = raw_planets[i]
                if g not in gate_to_planet: gate_to_planet[g] = []
                gate_to_planet[g].append(p_name)
                if p_name in ["North_Node", "South_Node"]:
                    nodes.add(g)
            
            person_gate_planet_map[name] = gate_to_planet
            if 'full_activations' not in locals(): full_activations = {}
            full_activations[name] = details.get("activations", {})
            
            person_nodes_map[name] = nodes
            
    group_size = len(processed_persons_dict)
    penta_info = None
    if 3 <= group_size <= 5:
        penta_info = get_penta_dynamics(person_gates_map)
        
    combinations_list = []
    if len(processed_persons_dict) >= 2:
        result_df = hd.get_composite_combinations(processed_persons_dict)
        combinations_list = result_df.to_dict(orient="records")
        
        for combo in combinations_list:
            if "new_chakra" in combo and isinstance(combo["new_chakra"], list):
                combo["new_chakra"] = [hd_constants.CHAKRA_NAMES_MAP.get(c, c) for c in combo["new_chakra"]]
            
            p1_name, p2_name = combo["id"], combo["other_person"]
            p1_gates = person_gates_map.get(p1_name, set())
            p2_gates = person_gates_map.get(p2_name, set())
            combined_gates = p1_gates.union(p2_gates)
            
            # --- Professional Maia Enrichments ---
            chakra_count = combo.get("chakra_count", 0)
            connection_label = get_connection_classification(chakra_count)
            combo["connection_code"] = connection_label
            
            new_channels = combo.get("new_channels", [])
            ch_meanings = combo.get("new_ch_meaning", [])
            
            maia_details = []
            circuitry_counts = {"Individual": 0, "Tribal": 0, "Collective": 0, "Integration": 0}
            flavors = []
            
            # Map channel list to (gate, ch_gate) to match constants
            for i, channel in enumerate(new_channels):
                g1, g2 = channel
                # Check circuitry
                c_key = tuple(sorted((g1, g2)))
                c_type_short = hd_constants.circuit_typ_dict.get(c_key, "Unknown")
                c_group = hd_constants.circuit_group_typ_dict.get(c_type_short, "Unknown")
                if c_group in circuitry_counts: circuitry_counts[c_group] += 1
                
                # Planetary Flavors
                p1_triggers = person_gate_planet_map.get(p1_name, {}).get(g1, ["None"]) + \
                             person_gate_planet_map.get(p1_name, {}).get(g2, ["None"])
                p2_triggers = person_gate_planet_map.get(p2_name, {}).get(g1, ["None"]) + \
                             person_gate_planet_map.get(p2_name, {}).get(g2, ["None"])
                             
                p1_flavor = [t for t in p1_triggers if t != "None"]
                p2_flavor = [t for t in p2_triggers if t != "None"]
                
                flavors.append(f"{'/'.join(p1_flavor)}-{'/'.join(p2_flavor)}")

                # Map activations for SubLineDetail
                maia_activations = []
                for p_name, act in full_activations.get(p1_name, {}).items():
                    if act["gate"] in channel:
                        maia_activations.append(act)
                for p_name, act in full_activations.get(p2_name, {}).items():
                    if act["gate"] in channel:
                        maia_activations.append(act)

                maia_details.append({
                    "channel": channel,
                    "meaning": ch_meanings[i] if i < len(ch_meanings) else "Unknown",
                    "type": classify_maia_connection(p1_gates, p2_gates, channel),
                    "circuitry": get_sub_circuit_detail(channel),
                    "planetary_trigger": f"P1:{'/'.join(p1_flavor)} | P2:{'/'.join(p2_flavor)}",
                    "activations": maia_activations
                })
            combo["maia_details"] = maia_details
            
            # --- Synergy Block (Ultra Professional 10x) ---
            p1_details = utc_birthdata_dict.get(p1_name, {})
            p2_details = utc_birthdata_dict.get(p2_name, {})
            
            is_bridged = (person_definition_map.get(p1_name, "1") != "1" or person_definition_map.get(p2_name, "1") != "1") and chakra_count >= 8
            
            # Love Gates logic (Gates 10, 15, 25, 46, 5, 14, 29 etc. - checking what's in constants)
            # Standard Love Gates of G: 10, 15, 25, 46 + Others
            love_gates_list = [10, 15, 25, 46, 5, 2, 29]
            active_love_gates = [g for g in love_gates_list if g in combined_gates]
            
            dynamics = calculate_center_dynamics(
                p1_details.get("defined_centers", []),
                p2_details.get("defined_centers", [])
            )
            space_count = list(dynamics.values()).count("open_window")
            
            combo["synergy"] = {
                "thematic_label": connection_label,
                "bridge_active": is_bridged,
                "center_dynamics": dynamics,
                "aura_dynamic": get_aura_dynamic(p1_details.get("energy_type"), p2_details.get("energy_type")),
                "love_gate_highlights": active_love_gates,
                "space_count": space_count,
                "circuitry_dominant": max(circuitry_counts, key=circuitry_counts.get) if any(circuitry_counts.values()) else "None",
                "profile_resonance": get_profile_resonance(p1_details.get("profile"), p2_details.get("profile")),
                "node_resonance": get_node_resonance(person_nodes_map.get(p1_name, set()), person_nodes_map.get(p2_name, set())),
                "dominant_sub_circuit": get_sub_circuit_detail(new_channels[0]) if new_channels else "Multiple/Neutral",
                "planetary_flavor_summary": flavors[0] if flavors else "Neutral",
                "group_dynamic_summary": f"Penta Structure ({group_size})" if penta_info else f"Pairwise ({group_size})",
                "penta_details": penta_info
            }

    return sanitize_for_json({"persons": utc_birthdata_dict, "combinations": combinations_list})
