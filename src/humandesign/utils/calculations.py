from .. import features as hd
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
    # We must mock the input for composite_chakras_channels.
    persons_dict = {
        "natal": birth_timestamp,
        "transit": transit_date_timestamp # We treat transit as another "person" for comparison
    }
    # This comparison highlights what is new *to the combination*
    new_channels, duplicated_channels, new_chakras, comp_chakras = hd.composite_chakras_channels(
        persons_dict, "natal", "transit") 
    
    # Extract offset from birth_timestamp for the birth_date conversion
    birth_offset = birth_timestamp[6] 
    
    # 6. Structure output
    return {
        "transit_date": to_iso_utc(transit_date_timestamp),
        "birth_date": clean_birth_date_to_iso(birth_features[9], birth_offset),
        "birth_place": birth_place,
        "composite_type": typ,
        "composite_authority": auth,
        "new_defined_channels": list(zip(new_channels["gate"], new_channels["ch_gate"])),
        "new_channel_meanings": list(new_channels["meaning"]),
        "new_defined_centers": list(new_chakras),
        "total_defined_centers": len(comp_chakras),
        "raw_transit_gates": day_gate_dict
    }
