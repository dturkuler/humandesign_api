from typing import Any, List, Optional, Set, Dict

class OutputMaskingService:
    @staticmethod
    def mask_dict(data: Dict[str, Any], include: Optional[List[str]] = None, exclude: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Filters a dictionary based on include and exclude sets.
        Recursive masking is not implemented for now as sections are top-level.
        """
        if not data:
            return data
            
        result = data.copy()
        
        # Determine valid keys
        keys = set(result.keys())
        
        if include:
            include_set = set(include)
            keys_to_remove = keys - include_set
            for k in keys_to_remove:
                result.pop(k, None)
        
        if exclude:
            for k in exclude:
                result.pop(k, None)
                
        return result

    @staticmethod
    def apply_mask(result: Dict[str, Any], include: Optional[List[str]] = None, exclude: Optional[List[str]] = None) -> Dict[str, Any]:
        """Entry point for masking logic."""
        return OutputMaskingService.mask_dict(result, include, exclude)
