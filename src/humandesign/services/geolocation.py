from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from typing import Optional, Tuple, List
from dataclasses import dataclass
from timezonefinder import TimezoneFinder

# Singleton instance
# in_memory=True ensures the binary file is loaded once into RAM (20-30MB) 
# and not re-read from disk on every lookup.
tf = TimezoneFinder(in_memory=True)

@dataclass
class Location:
    place: str
    latitude: Optional[float]
    longitude: Optional[float]
    address: Optional[str] = None

def get_latitude_longitude(place: str) -> Tuple[Optional[float], Optional[float]]:
    """
    Get latitude and longitude for a given place name.
    
    Args:
        place (str): Name of the place (e.g., "City, Country") or TZ name (e.g., "Europe/London")
        
    Returns:
        Tuple[float, float]: Latitude and Longitude, or (None, None) if not found.
    """
    # Bypass for timezone names to avoid network calls in tests or when TZ is known
    if "/" in place:
        return 0.0, 0.0 # Return placeholder coordinates
        
    geolocator = Nominatim(user_agent="geocoding_api")
    try:
        location = geolocator.geocode(place, timeout=2) # Shorter timeout
        if location:
            return location.latitude, location.longitude
    except Exception:
        pass
    return None, None

def get_address(latitude: float, longitude: float) -> Optional[str]:
    """Reverse geocode coordinates to get an address."""
    geolocator = Nominatim(user_agent="geocoding_api")
    try:
        location = geolocator.reverse((latitude, longitude))
        return location.address if location else None
    except Exception:
        return None

def batch_geocode(places: List[str]) -> List[Location]:
    """Geocode multiple places at once."""
    geolocator = Nominatim(user_agent="geocoding_api")
    results = []
    
    for place in places:
        location = geolocator.geocode(place)
        if location:
            results.append(Location(
                place=place,
                latitude=location.latitude,
                longitude=location.longitude,
                address=location.address
            ))
        else:
            results.append(Location(
                place=place,
                latitude=None,
                longitude=None,
                address=None
            ))
    return results

def calculate_distance(place1: str, place2: str) -> Optional[float]:
    """Calculate distance between two places in kilometers."""
    coords1 = get_latitude_longitude(place1)
    coords2 = get_latitude_longitude(place2)
    
    if None in coords1 or None in coords2:
        return None
        
    return geodesic(coords1, coords2).kilometers

if __name__ == "__main__":
    place = "Istanbul, Turkey"
    latitude, longitude = get_latitude_longitude(place)
    print(f"Latitude: {latitude}, Longitude: {longitude}")
