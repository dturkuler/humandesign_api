from typing import Any, List, Optional, Set, Dict

class OutputMaskingService:
    @staticmethod
    def _parse_dot_notation(paths: List[str]) -> Dict[str, Any]:
        """
        Parses a list of dot-notation strings into a nested dictionary structure.
        Example: ['a.b', 'a.c', 'd'] -> {'a': {'b': True, 'c': True}, 'd': True}
        """
        tree = {}
        for path in paths:
            parts = path.split('.')
            current = tree
            for i, part in enumerate(parts):
                is_last = (i == len(parts) - 1)
                
                if part not in current:
                    current[part] = {} if not is_last else True
                
                # If we land on a node that is already True, it means a parent was fully included
                if current[part] is True:
                    break
                    
                if is_last:
                    current[part] = True
                else:
                    current = current[part]
        return tree

    @staticmethod
    def _recursive_include(data: Any, spec: Dict[str, Any]) -> Any:
        """Recursively filters the dictionary based on the spec."""
        if spec is True:
            return data
        
        if isinstance(data, dict):
            result = {}
            for key, sub_spec in spec.items():
                if key in data:
                    result[key] = OutputMaskingService._recursive_include(data[key], sub_spec)
            return result
        return data

    @staticmethod
    def _recursive_exclude(data: Any, paths: List[str]) -> None:
        """Recursively removes fields specified by dot-notation paths."""
        for path in paths:
            parts = path.split('.')
            current = data
            for i, part in enumerate(parts[:-1]):
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    current = None
                    break
            
            if current is not None and isinstance(current, dict):
                last_part = parts[-1]
                if last_part in current:
                    del current[last_part]

    @staticmethod
    def mask_dict(data: Dict[str, Any], include: Optional[List[str]] = None, exclude: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Filters a dictionary based on include and exclude sets using dot-notation support.
        """
        if not data:
            return data
            
        import copy
        
        # 1. Apply Include (Whitelist)
        if include:
            spec = OutputMaskingService._parse_dot_notation(include)
            result = OutputMaskingService._recursive_include(data, spec)
        else:
            # Deepcopy to prevent mutation of original data during exclude phase
            result = copy.deepcopy(data)

        # 2. Apply Exclude (Blacklist)
        if exclude:
            OutputMaskingService._recursive_exclude(result, exclude)
                
        return result

    @staticmethod
    def apply_mask(result: Any, include: Optional[List[str]] = None, exclude: Optional[List[str]] = None) -> Dict[str, Any]:
        """Entry point for masking logic. Supports Pydantic models."""
        data = result if isinstance(result, dict) else result.model_dump(exclude_none=True)
        return OutputMaskingService.mask_dict(data, include, exclude)
