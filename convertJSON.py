import json
import re
import hd_constants

def get_incarnation_cross_map(input_string):
    """
    Parses string format: ((P_Sun, P_Earth), (D_Sun, D_Earth))-ANGLE
    Example: ((55, 59), (34, 20))-RAC
    Returns: The string name of the Cross.
    """
    try:
        # 1. Split the string to separate the Gates from the Angle
        # Split on ')-' to get ["((55, 59), (34, 20)", "RAC"]
        parts = input_string.split(")-")
        
        if len(parts) != 2:
            return "Error: Invalid input format. Expected format ((S, E), (S, E))-ANGLE"
            
        gates_part = parts[0]
        angle_part = parts[1].strip() # e.g., "RAC", "JC", "LAC"

        # 2. Extract the Personality Sun (The first number in the tuple)
        # We use Regex to find the first number after default parens
        # This looks for the first sequence of digits
        match = re.search(r'\d+', gates_part)
        
        if not match:
            return "Error: Could not parse Sun Gate number."
            
        p_sun_gate = int(match.group())

        # 3. Lookup in Constants Database
        gate_data = hd_constants.CROSS_DB.get(p_sun_gate)

        if not gate_data:
            return f"Error: Gate {p_sun_gate} not found in database."

        # 4. Return specific angle
        cross_name = gate_data.get(angle_part)
        
        if not cross_name:
            return f"Error: Angle '{angle_part}' not valid for Gate {p_sun_gate}."

        return cross_name

    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"

def get_profile_name(profile_list):
    """
    Parses list format: [Personality_Line, Design_Line]
    Example Input: [2, 4]
    Returns: "2/4: Hermit Opportunist"
    """
    try:
        # 1. Validate input is a list/tuple of length 2
        if not profile_list or len(profile_list) != 2:
            return "Error: Input must be a list of two integers."

        # 2. Convert list to tuple to use as dictionary key
        # (Lists are not hashable in Python, so we must use a tuple)
        key = tuple(profile_list)

        # 3. Lookup in Constants Database
        profile_name = hd_constants.PROFILE_DB.get(key)

        if not profile_name:
            return f"Error: Profile {key[0]}/{key[1]} does not exist."

        return profile_name

    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"




def general(data):
    # 1. Get the Energy Type (Calculated previously)
    e_type = data.get('energie_type', 'Unknown')
    
    # 2. Get the specific details for this Type from our new Map
    # We use .get() to safely default to "Unknown" if the type isn't found
    type_details = hd_constants.TYPE_DETAILS_MAP.get(e_type, hd_constants.TYPE_DETAILS_MAP["Unknown"])

    # 3. Construct Output
    output = {
        "birth_date": data['birth_date'],
        "create_date": data['create_date'],
        
        # --- Type Info ---
        "energie_type": e_type,
        "strategy": type_details['strategy'],     # <--- NEW
        "signature": type_details['signature'],   # <--- NEW (Goal)
        "not_self": type_details['not_self'],     # <--- NEW (Warning)
        "aura": type_details['aura'],             # <--- NEW
        # -----------------

        "inner_authority": hd_constants.INNER_AUTHORITY_NAMES_MAP.get(data['inner_authority'], data['inner_authority']),
        "inc_cross": get_incarnation_cross_map(data['inc_cross']),
        "profile": get_profile_name(data['profile']),
        
        "defined_centers": [hd_constants.CHAKRA_NAMES_MAP.get(chakra, chakra) for chakra in data['active_chakras']],
        "undefined_centers": [hd_constants.CHAKRA_NAMES_MAP.get(chakra, chakra) for chakra in data['inactive_chakras']],
        "split": hd_constants.SPLIT_DB.get(str(data['split']), data['split']),
        "variables": data['variables']
    }
    
    return json.dumps(output, indent=2)



def gatesJSON(data):
    # Initialize the structure for 'prs' and 'des'
    output = {
        "prs": {
            "Planets": []
        },
        "des": {
            "Planets": []
        }
    }

    # Loop through the data and populate 'prs' and 'des'
    for i in range(len(data['label'])):
        planet_data = {
            "Planet": data['planets'][i],
            "Lon": data['lon'][i],
            "Gate": data['gate'][i],
            "Line": data['line'][i],
            "Color": data['color'][i],
            "Tone": data['tone'][i],
            "Base": data['base'][i],
            "Ch_Gate": data['ch_gate'][i]
        }
        
        # Add planet data to the appropriate label ('prs' or 'des')
        if data['label'][i] == 'prs':
            output['prs']['Planets'].append(planet_data)
        else:
            output['des']['Planets'].append(planet_data)

    # Convert the result to JSON string (optional, for display purposes)
    return json.dumps(output, indent=2)

def get_channel_name(gate1, gate2):
    """
    Takes two gate numbers, sorts them, formats them as "LowGate/HighGate",
    and returns the full channel name from CHANNEL_DB.
    """
    try:
        # Ensure gates are integers
        g1 = int(gate1)
        g2 = int(gate2)

        # Sort the gates to create a consistent key
        sorted_gates = tuple(sorted((g1, g2)))
        key = f"{sorted_gates[0]}/{sorted_gates[1]}"

        # Lookup in Constants Database
        channel_name = hd_constants.CHANNEL_DB.get(key)

        if not channel_name:
            return f"Error: Channel {key} not found in database."

        return f"{key}: {channel_name}"

    except ValueError:
        return "Error: Gate numbers must be integers."
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"

def channelsJSON(data, details=False):
    # details: get all details or only channels numbers
    result = []
    
    # Extracting the arrays from the input data
    labels = data['label']
    planets = data['planets']
    gates = data['gate']
    ch_gates = data['ch_gate']
    gate_chakras = data['gate_chakra']
    ch_gate_chakras = data['ch_gate_chakra']
    ch_gate_labels = data['ch_gate_label']
    gate_labels = data['gate_label']

    # Creating the JSON structure based on the details flag
    for i in range(len(labels)):
        channel_full_name = get_channel_name(gates[i], ch_gates[i])
        if details:
            channel_data = {
                "channel": channel_full_name,  # Use full channel name
                "label": str(labels[i]),
                "planets": str(planets[i]),
                "gate": str(gates[i]),
                "ch_gate": str(ch_gates[i]),
                "ch_gate_chakra": str(ch_gate_chakras[i]),
                "ch_gate_chakra_label": [str(label) for label in ch_gate_labels[i]],
                "gate_label": [str(label) for label in gate_labels[i]],
                "gate_label_detail": str(gate_chakras[i])
            }
        else:
            channel_data = {
                "channel": channel_full_name  # Only include full channel name
            }
        result.append(channel_data)
    
    # Convert the result to a JSON string
    return json.dumps({"Channels": result}, indent=4)
