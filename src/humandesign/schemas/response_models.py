from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class VariableDetail(BaseModel):
    value: str
    name: str
    aspect: str
    def_type: str

class Variables(BaseModel):
    top_right: VariableDetail
    bottom_right: VariableDetail
    top_left: VariableDetail
    bottom_left: VariableDetail
    short_code: str = Field(..., description="Standard shorthand for all four variables (e.g., 'PRL DRR')")

class GeneralOutput(BaseModel):
    birth_date: str
    create_date: str
    birth_place: Optional[str] = None
    age: Optional[int] = Field(None, description="Calculated age in years")
    gender: Optional[str] = "male"
    islive: Optional[bool] = Field(True, description="Whether the person is still alive (True) or deceased (False)")
    zodiac_sign: Optional[str] = Field(None, description="Western astrological sign")
    energy_type: str
    inner_authority: str
    inc_cross: str
    profile: str
    active_chakras: List[str]
    inactive_chakras: List[str]
    definition: str
    variables: Variables

class GateInfo(BaseModel):
    gate: int
    line: int
    color: int
    tone: int
    base: int
    is_active: bool

class ChannelInfo(BaseModel):
    name: str
    gates: List[int]
    meaning: Optional[str] = None

class CalculateResponse(BaseModel):
    general: GeneralOutput
    channels: List[ChannelInfo]
    gates: Dict[str, List[GateInfo]]

class PentaDetail(BaseModel):
    active_skills: List[str]
    penta_gaps: List[str]
    is_functional: bool

class SubLineDetail(BaseModel):
    gate: int
    line: int
    color: int
    tone: int
    base: int
    planet: str

class MaiaDetail(BaseModel):
    channel: List[int] = Field(..., description="The two gates forming the channel")
    meaning: List[str] = Field(..., description="The spiritual and mechanical names of the channel")
    type: str = Field(..., description="Maia classification: Electromagnetic, Compromise, Dominance, or Companionship")
    circuitry: str = Field(..., description="The Human Design circuitry group (Individual, Tribal, Collective)")
    planetary_trigger: str = Field(..., description="The planets activating the gates in this connection")
    activations: List[SubLineDetail] = Field([], description="High-fidelity activation data (Gate, Line, Color, Tone, Base)")

class SynergyDetail(BaseModel):
    thematic_label: str = Field(..., description="Professional Maian theme (e.g. '8-1 Have some fun')")
    bridge_active: bool = Field(..., description="True if this combination bridges a split definition")
    center_dynamics: Dict[str, str] = Field(..., description="Conditioning dynamic for each center (fixed, conditioning_p1_to_p2, etc.)")
    aura_dynamic: str = Field(..., description="Professional label for Type-to-Type energetic interaction")
    love_gate_highlights: List[int] = Field(..., description="List of active G-Center love gates in the connection")
    space_count: int = Field(..., description="Number of completely open centers in the composite (Relational Space)")
    circuitry_dominant: str = Field(..., description="The dominant circuitry group in the partnership")
    profile_resonance: str = Field(..., description="Resonance or Harmony level between the two profiles")
    node_resonance: str = Field(..., description="Resonance level between the South and North Nodes (Environmental Fit)")
    dominant_sub_circuit: str = Field(..., description="Maximum detail on the sub-circuitry (e.g., Knowing vs. Logical)")
    planetary_flavor_summary: str = Field(..., description="The dominant planetary quality of the attraction (e.g., Venus-Mars)")
    group_dynamic_summary: str = Field(..., description="Classification of the group structure (Dyad, Penta, Wa)")
    penta_details: Optional[PentaDetail] = Field(None, description="Detailed Penta dynamics for groups of 3-5")

class CombinationItem(BaseModel):
    id: str
    other_person: str
    new_chakra: List[str]
    chakra_count: int
    new_channels: List[List[int]]
    new_ch_meaning: List[str]
    connection_code: str = Field(..., description="The 9-0 etc. connection classification code")
    maia_details: List[MaiaDetail] = Field(..., description="Deep Maian connection types for each channel")
    synergy: SynergyDetail = Field(..., description="Professional synergy and conditioning dynamics")

class CompositePersonDetail(BaseModel):
    name: str
    place: str
    tz: str
    birth_date: str
    create_date: str
    energy_type: str
    strategy: Optional[str] = None
    signature: Optional[str] = None
    not_self: Optional[str] = None
    aura: Optional[str] = None
    inner_authority: str
    inc_cross: str
    profile: str
    defined_centers: List[str]
    undefined_centers: List[str]
    definition: str
    variables: Optional[Variables] = None
    lunar_context: Optional[str] = Field(None, description="Lunar phase at birth")
    activations: Optional[Dict[str, SubLineDetail]] = Field(None, description="Full planetary activation matrix")
    channels: List[Dict]

class CompMatrixResponse(BaseModel):
    persons: Dict[str, CompositePersonDetail]
    combinations: List[CombinationItem]
