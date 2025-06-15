VALID_DIGITS = {
    2:  "01",
    8:  "01234567",
    10: "0123456789",
    16: "0123456789ABCDEF"
}

def int_to_base(number, base):
    if not 2 <= base <= 36:
        raise ValueError(f"База должна быть от 2 до 36, получено: {base}")
    
    if number == 0:
        return "0"
        
    digits = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    negative = number < 0
    number = abs(number)
    
    result = ""
    while number:
        result = digits[number % base] + result
        number //= base
        
    return "-" + result if negative else result

def base_to_int(value_str, base):
    if not 2 <= base <= 36:
        raise ValueError(f"База должна быть от 2 до 36, получено: {base}")
        
    try:
        return int(value_str, base)
    except ValueError:
        raise ValueError(f"Неверное число '{value_str}' для системы счисления {base}")
