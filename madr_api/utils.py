def sanitize_string(old_str: str) -> str:
    sanitized = old_str.lower().strip()
    sanitized = ' '.join(sanitized.split())
    return sanitized
