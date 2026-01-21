from typing import Dict, Any, List, Optional
from .sqlite_repository import SQLiteRepository

class EnrichmentService:
    def __init__(self):
        self.repo = SQLiteRepository()

    def enrich_gate(self, gate_number: int, line_number: int, planet_name: str) -> Dict[str, Any]:
        """
        Fetches semantic data and attempts to determine fixation.
        """
        gate_info = self.repo.get_gate_label(gate_number)
        line_info = self.repo.get_line_label(gate_number, line_number)
        
        # Simple Fixation Parser (Logic based on description text)
        fixation = self._parse_fixation(line_info.get("description", ""), planet_name)
        
        return {
            "gate_name": gate_info.get("name"),
            "gate_summary": gate_info.get("summary"),
            "line_name": line_info.get("name"),
            "line_description": line_info.get("description"),
            "fixation": fixation
        }

    def _parse_fixation(self, description: str, planet_name: str) -> Optional[Dict[str, Any]]:
        """
        Heuristic: Look for 'PlanetName exalted' or 'PlanetName in detriment'.
        This is a temporary parser until a structured table is found/provided.
        """
        if not description:
            return None
            
        desc_lower = description.lower()
        planet_lower = planet_name.lower()
        
        # Check for Exaltation
        if f"{planet_lower} exalted" in desc_lower or f"{planet_lower} as a symbol of" in desc_lower:
            return {"type": "Exalted", "value": "Up"}
        
        # Check for Detriment
        if f"{planet_lower} in detriment" in desc_lower or f"detriment of {planet_lower}" in desc_lower:
            return {"type": "Detriment", "value": "Down"}
            
        return None

    def enrich_response(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recursively enrich the response structure.
        """
        for gate_key in ["personality_gates", "design_gates"]:
            if gate_key in response_data and response_data[gate_key]:
                for planet, gate_data in response_data[gate_key].items():
                    if isinstance(gate_data, dict):
                        enriched = self.enrich_gate(
                            gate_data.get("gate"), 
                            gate_data.get("line"),
                            planet
                        )
                        gate_data.update(enriched)
                    else:
                        # If it's a Pydantic model
                        enriched = self.enrich_gate(gate_data.gate, gate_data.line, planet)
                        gate_data.gate_name = enriched.get("gate_name")
                        gate_data.gate_summary = enriched.get("gate_summary")
                        gate_data.line_name = enriched.get("line_name")
                        gate_data.line_description = enriched.get("line_description")
                        gate_data.fixation = enriched.get("fixation")
                    
        return response_data
