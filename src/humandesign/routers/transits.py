from fastapi import APIRouter, Query, HTTPException, Depends
from timezonefinder import TimezoneFinder
from .. import features as hd
from ..services.geolocation import get_latitude_longitude
from ..dependencies import verify_token
from ..utils.calculations import process_transit_data

router = APIRouter(prefix="/transits", tags=["transits"])

@router.get("/solar_return")
def get_solar_return(
    year: int = Query(..., description="Birth year"),
    month: int = Query(..., description="Birth month"),
    day: int = Query(..., description="Birth day"),
    hour: int = Query(..., description="Birth hour"),
    minute: int = Query(0, description="Birth minute (default 0)"),
    second: int = Query(0, description="Birth second (optional, default 0)"),
    place: str = Query(..., description="Birth place (city, country)"),
    sr_year_offset: int = Query(0, description="Calculate Solar Return for X years after birth. 0 is the current SR."),
    authorized: bool = Depends(verify_token)
):
    # Geocoding and timezone logic
    latitude, longitude = get_latitude_longitude(place)
    if latitude is None or longitude is None:
        raise HTTPException(status_code=400, detail=f"Geocoding failed for place: '{place}'")
    tf = TimezoneFinder()
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
    
    return {
        "solar_return_year": sr_year_offset,
        "solar_return_utc_date": f"{int(sr_year)}-{int(sr_month):02d}-{int(sr_day):02d}T{int(sr_hour):02d}:{int(sr_minute):02d}:{int(sr_second):02d}Z",
        "sr_chart_analysis": sr_composite_data
    }


@router.get("/daily")
def get_daily_transit(
    year: int = Query(..., description="Birth year"),
    month: int = Query(..., description="Birth month"),
    day: int = Query(..., description="Birth day"),
    hour: int = Query(..., description="Birth hour"),
    minute: int = Query(0, description="Birth minute (default 0)"),
    second: int = Query(0, description="Birth second (optional, default 0)"),
    place: str = Query(..., description="Birth place (city, country)"),
    transit_year: int = Query(..., description="Transit year to analyze"),
    transit_month: int = Query(..., description="Transit month to analyze"),
    transit_day: int = Query(..., description="Transit day to analyze"),
    authorized: bool = Depends(verify_token)
):
    # Geocoding/timezone for the BIRTH location
    latitude, longitude = get_latitude_longitude(place)
    if latitude is None or longitude is None:
        raise HTTPException(status_code=400, detail=f"Geocoding failed for place: '{place}'")
    tf = TimezoneFinder()
    zone = tf.timezone_at(lat=latitude, lng=longitude) or 'Etc/UTC'
    birth_time = (year, month, day, hour, minute, second)
    hours = hd.get_utc_offset_from_tz(birth_time, zone)
    birth_timestamp = tuple(list(birth_time) + [int(hours)])

    # Transit timestamp (uses Birth location's local time/offset for the analysis moment)
    transit_time = (transit_year, transit_month, transit_day, birth_time[3], birth_time[4], birth_time[5])
    transit_timestamp = tuple(list(transit_time) + [int(hours)])

    # Calculate the composite chart at the transit moment
    composite_data = process_transit_data(transit_timestamp, birth_timestamp, place)

    return {
        "transit_date": f"{transit_year}-{transit_month:02d}-{transit_day:02d}",
        "transit_time_at_birth_location": f"{birth_time[3]:02d}:{birth_time[4]:02d}",
        "analysis": composite_data
    }
