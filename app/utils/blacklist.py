# app/utils/blacklist.py

_BLACKLIST = set()

def add_to_blacklist(jti: str):
    _BLACKLIST.add(jti)

def is_blacklisted(jti: str) -> bool:
    return jti in _BLACKLIST
