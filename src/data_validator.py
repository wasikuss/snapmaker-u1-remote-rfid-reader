
import json

class DataValidator:
    ALLOWED_KEYS = {'brand', 'type', 'subtype', 'color_hex', 'alpha', 'min_temp', 'max_temp', 'bed_min_temp', 'bed_max_temp'}
    @staticmethod
    def validate(data, strict=False):
        if not isinstance(data, str) or not data.strip():
            return False
        try:
            parsed = json.loads(data)
            if not isinstance(parsed, dict):
                return False
            
            if strict:
                for key in DataValidator.ALLOWED_KEYS:
                    if key not in parsed:
                        print(f"Missing key in data: {key}")
                        return False
                for key in parsed:
                    if key not in DataValidator.ALLOWED_KEYS:
                        print(f"Unexpected key in data: {key}")
                        return False

            return True
        except json.JSONDecodeError:
            return False