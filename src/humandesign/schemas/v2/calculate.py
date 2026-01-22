from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, EmailStr

class CalculateRequestV2(BaseModel):
    year: int = Field(1968, description="Birth year")
    month: int = Field(2, description="Birth month")
    day: int = Field(21, description="Birth day")
    hour: int = Field(11, description="Birth hour")
    minute: int = Field(0, description="Birth minute")
    second: int = Field(0, description="Birth second")
    place: str = Field("Kirikkale, Turkey", description="Birth place")
    gender: Optional[str] = Field("male", description="Gender")
    islive: Optional[bool] = Field(True, description="Whether alive")
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    include: Optional[List[str]] = Field(None, description="Sections to include (e.g. ['general', 'personality_gates'])", example=["general", "personality_gates"])
    exclude: Optional[List[str]] = Field(None, description="Sections to exclude", example=["channels"])

class VariableItemV2(BaseModel):
    value: Optional[str] = None
    name: Optional[str] = None
    aspect: Optional[str] = None
    def_type: Optional[str] = None

class VariablesV2(BaseModel):
    top_right: Optional[VariableItemV2] = None
    bottom_right: Optional[VariableItemV2] = None
    top_left: Optional[VariableItemV2] = None
    bottom_left: Optional[VariableItemV2] = None
    short_code: Optional[str] = None

class CentersV2(BaseModel):
    defined: Optional[List[str]] = None
    undefined: Optional[List[str]] = None

class GatesV2(BaseModel):
    personality: Optional[Dict[str, 'GateV2']] = None
    design: Optional[Dict[str, 'GateV2']] = None

class GeneralSectionV2(BaseModel):
    birth_date: Optional[str] = None
    create_date: Optional[str] = None
    birth_place: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    islive: Optional[bool] = None
    zodiac_sign: Optional[str] = None
    energy_type: Optional[str] = None
    strategy: Optional[str] = None
    signature: Optional[str] = None
    not_self: Optional[str] = None
    aura: Optional[str] = None
    inner_authority: Optional[str] = None
    inc_cross: Optional[str] = None
    profile: Optional[str] = None
    definition: Optional[str] = None

class GateV2(BaseModel):
    gate: int
    line: int
    color: int
    tone: int
    base: int
    lon: float
    gate_name: Optional[str] = None
    gate_summary: Optional[str] = None
    line_name: Optional[str] = None
    line_description: Optional[str] = None
    fixation: Optional[Dict[str, Any]] = None

class DreamRaveOutput(BaseModel):
    activated_centers: List[str]
    activated_gates: List[int]
    status: str

class GlobalCycleOutput(BaseModel):
    great_cycle: str
    cycle_cross: str
    gates: List[int]
    description: str

class AdvancedSectionV2(BaseModel):
    dream_rave: Optional[DreamRaveOutput] = None
    global_cycle: Optional[GlobalCycleOutput] = None

class CalculateResponseV2(BaseModel):
    general: Optional[GeneralSectionV2] = None
    centers: Optional[CentersV2] = None
    channels: Optional[List[Dict[str, Any]]] = None
    variables: Optional[VariablesV2] = None
    gates: Optional[GatesV2] = None
    mechanics: Optional[Dict[str, Any]] = None
    advanced: Optional[AdvancedSectionV2] = None
