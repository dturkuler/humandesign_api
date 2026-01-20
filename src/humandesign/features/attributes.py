from .. import hd_constants

def get_inc_cross(date_to_gate_dict):
    ''' 
    get incarnation cross from open gates 
        Args:
            date_to_gate_dict(dict):output of hd_feature class 
                                    keys->[planets,label,longitude,gate,line,color,tone,base]
        Return:
            incarnation cross(tuple): gates of sun and earth from birth and create date 
                                      format e.g. ((1,2),(3,4))
    '''
    df = date_to_gate_dict
    idx = int(len(df["planets"])/2) #start idx of design values 
    inc_cross = (
        (df["gate"][0],df["gate"][1]),#sun&earth gate at birth
        (df["gate"][idx],df["gate"][idx+1])#sun&earth gate at design
                )          
    profile = df["line"][0],df["line"][idx]
    cr_typ = hd_constants.IC_CROSS_TYP[profile]
    inc_cross = str(inc_cross)+"-"+cr_typ
    return inc_cross

def get_profile(date_to_gate_dict):
    ''' 
    profile is calculated from sun line of birth and design date
    Args:
        date_to_gate_dict(dict):output of hd_feature class 
                                    keys->[planets,label,longitude,gate,line,color,tone,base]
    Return:
        profile(tuple): format e.g. (1,4)
    '''
    df = date_to_gate_dict
    idx = int(len(df["line"])/2) #start idx of design values
    profile = (df["line"][0],df["line"][idx]) #sun gate at birth and design
    #sort lines to known format
    if profile not in hd_constants.IC_CROSS_TYP.keys():
        profile = profile[::-1]
    
    return profile

def get_variables(date_to_gate_dict):
    '''
    variables are calculated based on tones of sun(birth,design) and 
    Nodes(birth,design), respectively
    If tone 1,2,3-> left arrow, else right arrow
    Args:
        date_to_gate_dict(dict):output of hd_feature class 
                                    keys->[planets,label,longitude,gate,line,color,tone,base]
    Return:
        variables(dict): keys-> ["top_right","bottom_right","top_left","bottom_left"]
    '''
    df = date_to_gate_dict
    idx = int(len(df["tone"])/2) #start idx of design values 
    tones = (
            (df["tone"][0]),#sun at birth
            (df["tone"][3]),#Node at birth
            (df["tone"][idx]),#sun at design
            (df["tone"][idx+3]),#node at design
                ) 
    keys = ["top_right","bottom_right","top_left","bottom_left"] #arrows,variables
    
    variables = {}
    for i, key in enumerate(keys):
        tone = tones[i]
        val = "left" if tone <= 3 else "right"
        
        # Get metadata from constants
        meta = hd_constants.VARIABLES_METADATA.get(key, {})
        def_type = meta.get("definitions", {}).get(val, {}).get("type", "Unknown")
        
        variables[key] = {
            "value": val,
            "name": meta.get("name", "Unknown"),
            "aspect": meta.get("aspect", "Unknown"),
            "def_type": def_type
        }

    # Calculate Standard Shorthand (e.g., "PRL DRR")
    # Tones: 0:Motivation(P-Top), 1:Perspective(P-Bottom), 2:Digestion(D-Top), 3:Environment(D-Bottom)
    p_top = "R" if tones[0] > 3 else "L"
    p_bot = "R" if tones[1] > 3 else "L"
    d_top = "R" if tones[2] > 3 else "L"
    d_bot = "R" if tones[3] > 3 else "L"
    
    variables["short_code"] = f"P{p_top}{p_bot} D{d_top}{d_bot}"

    return variables 

def get_lunar_phase(date_to_gate_dict):
    """
    Calculate Lunar Phase from Sun/Moon longitude.
    Phase = (Moon - Sun) % 360
    """
    try:
        planets = date_to_gate_dict.get("planets", [])
        lons = date_to_gate_dict.get("lon", [])
        
        if "Sun" not in planets or "Moon" not in planets:
             return "Unknown"
             
        sun_idx = planets.index("Sun")
        moon_idx = planets.index("Moon")
        
        sun = lons[sun_idx]
        moon = lons[moon_idx]
        
        diff = (moon - sun) % 360
        
        # 8 Phases (approx 45 deg each)
        if diff < 45:
            return "New Moon"
        if diff < 90:
            return "Waxing Crescent"
        if diff < 135:
            return "First Quarter"
        if diff < 180:
            return "Waxing Gibbous"
        if diff < 225:
            return "Full Moon"
        if diff < 270:
            return "Waning Gibbous"
        if diff < 315:
            return "Last Quarter"
        return "Waning Crescent"
        
    except Exception:
        return "Unknown"

