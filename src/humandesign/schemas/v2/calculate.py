from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, EmailStr

class CalculateRequestV2(BaseModel):
    year: int = Field(..., description="Birth year")
    month: int = Field(..., description="Birth month")
    day: int = Field(..., description="Birth day")
    hour: int = Field(..., description="Birth hour")
    minute: int = Field(..., description="Birth minute")
    second: int = Field(0, description="Birth second")
    place: str = Field(..., description="Birth place")
    gender: Optional[str] = Field("male", description="Gender")
    islive: Optional[bool] = Field(True, description="Whether alive")
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    include: Optional[List[str]] = Field(None, description="Sections to include (e.g. ['general', 'mechanics'])")
    exclude: Optional[List[str]] = Field(None, description="Sections to exclude")

class VariableItemV2(BaseModel):
    value: str
    name: str
    aspect: str
    def_type: str

class VariablesV2(BaseModel):
    top_right: VariableItemV2
    bottom_right: VariableItemV2
    top_left: VariableItemV2
    bottom_left: VariableItemV2
    short_code: str

class GeneralSectionV2(BaseModel):
    birth_date: str
    create_date: str
    birth_place: str
    energy_type: str
    inner_authority: str
    inc_cross: str
    profile: str
    active_chakras: List[str]
    inactive_chakras: List[str]
    definition: str
    variables: VariablesV2
    age: int
    zodiac_sign: str
    gender: str
    islive: bool

class GateV2(BaseModel):
    gate: int
    line: int
    color: int
    tone: int
    base: int
    lon: float
    fixation: Optional[Dict[str, Any]] = None # To be populated in Phase 2

class CalculateResponseV2(BaseModel):
    general: Optional[GeneralSectionV2] = None
    mechanics: Optional[Dict[str, Any]] = None # To be populated in Phase 2
    advanced: Optional[Dict[str, Any]] = None # To be populated in Phase 3
    gates: Optional[Dict[str, GateV2]] = None
    channels: Optional[List[Dict[str, Any]]] = None
