def detect_language_code(text: str) -> str:
    """Detect very simply: hi if Devanagari, ta if Tamil, else en."""
    if not text:
        return "en"
    # Script-based quick detection first
    for ch in text:
        code = ord(ch)
        # Devanagari block
        if 0x0900 <= code <= 0x097F:
            return "hi"
        # Tamil block
        if 0x0B80 <= code <= 0x0BFF:
            return "ta"
    # Heuristic for romanized Hindi/Tamil
    t = text.lower()
    roman_hi = {
        "hai","kitna","kitni","kya","kyun","kaun","kahan","mein","hain","tha","thi","hoga","hogaya","kripya","dhanyavad"
    }
    roman_ta = {
        "irukku","ethana","evlo","enna","epdi","ungal","ungalukku","nalla","velai","sapadu"
    }
    # token match
    tokens = set(t.replace('?', ' ').replace('!', ' ').replace('.', ' ').split())
    if tokens & roman_hi:
        return "hi"
    if tokens & roman_ta:
        return "ta"
    return "en"

def language_name(code: str) -> str:
    return {"hi": "Hindi", "ta": "Tamil", "en": "English"}.get(code, "English")


