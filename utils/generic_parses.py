

def _parse_salary(s: str):
    if not s:
        return None, None
    try:
        if '-' in s:
            parts = [p.strip().replace('R$','').replace(',','') for p in s.split('-', 1)]
            return float(parts[0]), float(parts[1]) if parts[1] else None
        v = s.strip().replace('R$','').replace(',','')
        return float(v), float(v)
    except Exception:
        return None, None