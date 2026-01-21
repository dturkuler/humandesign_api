from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
import json

from ... import features as hd
from ... import hd_constants
from ...utils import serialization as cj
from ...services.geolocation import get_latitude_longitude, tf
from ...dependencies import verify_token
from ...utils.date_utils import clean_birth_date_to_iso, clean_create_date_to_iso
from ...schemas.v2.calculate import CalculateRequestV2, CalculateResponseV2, GeneralSectionV2, GateV2, AdvancedSectionV2, CentersV2
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
        # Get type details for semantic fields
        type_details = hd_constants.TYPE_DETAILS_MAP.get(single_result[0], hd_constants.TYPE_DETAILS_MAP["Unknown"])
        
        # Map chakra abbreviations to full names
        chakra_map = {
            "HD": "Head", "AA": "Ajna", "TT": "Throat", "GC": "G_Center",
            "HT": "Heart", "SN": "Spleen", "SP": "Solar Plexus",
            "SL": "Sacral", "RT": "Root"
        }
        
        # Get full names for centers
        active_chakras_abbr = list(single_result[7])
        inactive_chakras_abbr = list(set(hd_constants.CHAKRA_LIST) - set(single_result[7]))
        defined_centers = [chakra_map.get(c, c) for c in active_chakras_abbr]
        undefined_centers = [chakra_map.get(c, c) for c in inactive_chakras_abbr]
        
        # Get full profile name
        profile_tuple = tuple(single_result[4])
        profile_full = hd_constants.PROFILE_DB.get(profile_tuple, f"{single_result[4][0]}/{single_result[4][1]}")
        
        # Get full definition name
        definition_full = hd_constants.DEFINITION_DB.get(str(single_result[5]), str(single_result[5]))
        
        # Get full authority name (map abbreviations)
        authority_map = {
            "SP": "Emotional Authority",
            "SL": "Sacral Authority",
            "SN": "Splenic Authority",
            "HT": "Ego Authority",
            "GC": "Self-Projected Authority",
            "outher auth": "Outer Authority",
            "no auth": "Mental Authority (Outer Authority)"
        }
        authority_full = authority_map.get(single_result[1], single_result[1])
        
        # Get full incarnation cross name
        cross_tuple = single_result[2]  # Format: ((gate1, gate2), (gate3, gate4))-TYPE
        cross_type = single_result[3]  # RAC, LAC, or JC
        
        # Parse the cross to get the sun gate
        import re
        match = re.match(r"\(\((\d+), (\d+)\), \((\d+), (\d+)\)\)-(.+)", str(cross_tuple))
        if match:
            sun_gate = int(match.group(1))
            cross_abbr = match.group(5)
            cross_full = hd_constants.CROSS_DB.get(sun_gate, {}).get(cross_abbr, str(cross_tuple))
        else:
            cross_full = str(cross_tuple)
        
        # Build General Section
        general_data = {
            "birth_date": clean_birth_date_to_iso(single_result[9], hours),
            "create_date": clean_create_date_to_iso(single_result[10]),
            "birth_place": request.place,
            "age": age,
            "gender": request.gender or "male",
            "islive": request.islive if request.islive is not None else True,
            "zodiac_sign": zodiac_sign,
            "energy_type": single_result[0],
            "strategy": type_details["strategy"],
            "signature": type_details["signature"],
            "not_self": type_details["not_self"],
            "aura": type_details["aura"],
            "inner_authority": authority_full,
            "inc_cross": cross_full,
            "profile": profile_full,
            "definition": definition_full
        }
        
        # Build Centers Section
        centers_data = {
            "defined": defined_centers,
            "undefined": undefined_centers
        }
        
        # Build Gates Section
        raw_gates = single_result[6]
        pers_gates = {}
        dest_gates = {}
        
        # In single_result[6], first 13 are Personality ('prs'), next 13 are Design ('des')
        planet_list = raw_gates['planets']
        half = len(planet_list) // 2
        
        for i in range(half):
            p_name = planet_list[i]
            pers_gates[p_name] = GateV2(
                gate=raw_gates['gate'][i],
                line=raw_gates['line'][i],
                color=raw_gates['color'][i],
                tone=raw_gates['tone'][i],
                base=raw_gates['base'][i],
                lon=raw_gates['lon'][i]
            )
            
        for i in range(half, len(planet_list)):
            p_name = planet_list[i]
            dest_gates[p_name] = GateV2(
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
        full_response = CalculateResponseV2(
            general=GeneralSectionV2(**general_data),
            centers=CentersV2(**centers_data),
            variables=single_result[11],
            channels=channels_v2,
            personality_gates=pers_gates,
            design_gates=dest_gates,
            mechanics=None,
            advanced=None
        )
        
        # Apply Enrichment
        from ...services.enrichment import EnrichmentService
        from ...services.dream_rave import DreamRaveEngine
        from ...services.global_cycles import GlobalCycleEngine
        from datetime import date
        
        # --- Phase 2: Enrichment ---
        enrichment_service = EnrichmentService()
        enriched_response = enrichment_service.enrich_response(full_response)
        
        # --- Phase 3: Advanced Mechanics ---
        dream_engine = DreamRaveEngine()
        cycle_engine = GlobalCycleEngine()
        
        # Prepare data for Dream Rave (using simple set of gate numbers)
        all_active_gates = set()
        for v in enriched_response.personality_gates.values():
            all_active_gates.add(v.gate)
        for v in enriched_response.design_gates.values():
            all_active_gates.add(v.gate)
        
        dream_out = dream_engine.analyze(all_active_gates)
        
        # Calculate date for Global Cycles
        calc_date = date(request.year, request.month, request.day)
        cycle_out = cycle_engine.get_cycle(calc_date)
        
        enriched_response.advanced = AdvancedSectionV2(
            dream_rave=dream_out,
            global_cycle=cycle_out
        )

        # --- Output Masking ---
        # Apply Masking
        masked_response = OutputMaskingService.apply_mask(
            enriched_response, 
            include=request.include, 
            exclude=request.exclude
        )
        
        return masked_response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing V2 results: {str(e)}")
