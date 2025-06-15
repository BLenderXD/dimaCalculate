from core.converter import base_to_int

class Operand:
    def __init__(self, value_str: str, base: int):
        self.value_str = value_str
        self.base = base
        self._int_value = int(value_str, base)
        
    def to_int(self):
        """Преобразование в десятичное число"""
        return int(self.value_str, self.base)
        
        
    def __repr__(self):
        subscripts = {2: '₂', 8: '₈', 10: '₁₀', 16: '₁₆'}
        return f"{self.value_str}{subscripts[self.base]}"
