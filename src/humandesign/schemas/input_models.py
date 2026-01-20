from pydantic import BaseModel, Field, validator, field_validator
from typing import Union, Dict, Optional

# Input Model
class PersonInput(BaseModel):
    place: str = Field(..., min_length=1, description="Place of birth (City, Country)")
    year: Union[int, str] = Field(..., description="Birth year (1800-2100)")
    month: Union[int, str] = Field(..., description="Birth month (1-12)")
    day: Union[int, str] = Field(..., description="Birth day (1-31)")
    hour: Union[int, str] = Field(..., description="Birth hour (0-23)")
    minute: Union[int, str] = Field(..., description="Birth minute (0-59)")
    gender: str = Field("male", description="Gender (e.g., male, female, other)")
    islive: bool = Field(True, description="Whether the person is still alive (True) or deceased (False)")
    latitude: Union[float, None] = Field(None, description="Optional: Latitude for direct input (bypassing geocoding)")
    longitude: Union[float, None] = Field(None, description="Optional: Longitude for direct input (bypassing geocoding)")

    @field_validator('latitude')
    @classmethod
    def validate_latitude(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and (v < -90 or v > 90):
            raise ValueError('Latitude must be between -90 and 90')
        return v

    @field_validator('longitude')
    @classmethod
    def validate_longitude(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and (v < -180 or v > 180):
            raise ValueError('Longitude must be between -180 and 180')
        return v


    @validator('year', 'month', 'day', 'hour', 'minute', pre=True)
    def parse_int(cls, v):
        if isinstance(v, str):
            if not v.strip():
                raise ValueError("Empty string not allowed")
            return int(v)
        return v

    @validator('year')
    def validate_year_range(cls, v):
        if not (1800 <= v <= 2100):
            raise ValueError(f"Year {v} must be between 1800 and 2100")
        return v
    
    @validator('month')
    def validate_month_range(cls, v):
        if not (1 <= v <= 12):
            raise ValueError(f"Month {v} must be between 1 and 12")
        return v
        
    @validator('hour')
    def validate_hour_range(cls, v):
         if not (0 <= v <= 23):
            raise ValueError(f"Hour {v} must be between 0 and 23")
         return v

    @validator('minute')
    def validate_minute_range(cls, v):
         if not (0 <= v <= 59):
            raise ValueError(f"Minute {v} must be between 0 and 59")
         return v

    @validator('day')
    def validate_day_of_month(cls, v, values):
        # v is already int due to parse_int
        year = values.get('year')
        month = values.get('month')
        if year is None or month is None or not isinstance(year, int) or not isinstance(month, int):
            # If previous validations failed, skip complex logic
            return v
        
        if not (1 <= v <= 31):
             raise ValueError(f"Day {v} must be between 1 and 31")

        # Standard days per month
        days_in_month = {
            1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30,
            7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31
        }
        
        # Leap year check
        if month == 2 and (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)):
            days_in_month[2] = 29
            
        if v > days_in_month.get(month, 31):
             raise ValueError(f"Invalid day {v} for month {month} in year {year}")
        return v

class PentaRequest(BaseModel):
    participants: Dict[str, PersonInput] = Field(..., description="Dictionary of participants (3-5 people)")
    group_type: str = Field("family", description="Type of group analysis: 'family' (default) or 'business'")

    @validator('group_type')
    def validate_group_type(cls, v):
        allowed = ['family', 'business']
        if v.lower() not in allowed:
            raise ValueError(f"group_type must be one of {allowed}")
        return v.lower()

class HybridAnalysisRequest(BaseModel):
    participants: Dict[str, PersonInput] = Field(..., description="Dictionary of participants (2+ people)")
    group_type: str = Field("family", description="Type of group analysis: 'family' (default) or 'business'")
    verbosity: str = Field("all", description="Detail level: 'all' (default) or 'partial'")

    @validator('group_type')
    def validate_group_type(cls, v):
        allowed = ['family', 'business']
        if v.lower() not in allowed:
            raise ValueError(f"group_type must be one of {allowed}")
        return v.lower()

    @validator('verbosity')
    def validate_verbosity(cls, v):
        allowed = ['all', 'partial']
        if v.lower() not in allowed:
            raise ValueError(f"verbosity must be one of {allowed}")
        return v.lower()
