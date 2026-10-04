"""Emergency helplines by location (Help You Need feature).

Flow: user types a city/area -> Nominatim geocodes it (with address details)
-> we read country + province -> return the right emergency numbers.
If geocoding fails (offline / unknown place) the UI falls back to a country picker,
so the numbers are always reachable.
"""
import requests

URL = "https://nominatim.openstreetmap.org/search"
HEADERS = {"User-Agent": "CuraGlide/1.0"}

# ---- Pakistan: depends on province ---------------------------------------
PK_RESCUE_1122 = ("Rescue 1122 (Ambulance / Fire / Rescue)", "1122")
PK_EDHI = ("Edhi Ambulance", "115")
PK_CHHIPA = ("Chhipa Ambulance", "1020")
PK_AMAN = ("Aman Ambulance (Karachi)", "1021")
PK_POLICE = ("Police", "15")
PK_FIRE = ("Fire Brigade", "16")
PK_MENTAL = ("Umang Mental Health Helpline", "0311-7786264")

PAKISTAN = {
    "punjab": [PK_RESCUE_1122, PK_EDHI, PK_POLICE, PK_FIRE, PK_MENTAL],
    "khyber pakhtunkhwa": [PK_RESCUE_1122, PK_EDHI, PK_POLICE, PK_FIRE, PK_MENTAL],
    "islamabad": [PK_RESCUE_1122, PK_EDHI, PK_POLICE, PK_FIRE, PK_MENTAL],
    "azad": [PK_RESCUE_1122, PK_EDHI, PK_POLICE, PK_FIRE, PK_MENTAL],
    "gilgit": [PK_RESCUE_1122, PK_EDHI, PK_POLICE, PK_FIRE, PK_MENTAL],
    "sindh": [PK_EDHI, PK_CHHIPA, PK_AMAN, PK_RESCUE_1122, PK_POLICE, PK_FIRE, PK_MENTAL],
    "balochistan": [PK_EDHI, PK_RESCUE_1122, PK_POLICE, PK_FIRE, PK_MENTAL],
}
PAKISTAN_DEFAULT = [PK_EDHI, PK_RESCUE_1122, PK_POLICE, PK_FIRE, PK_MENTAL]

# ---- Other countries: ISO code -> (country name, [(label, number)]) --------
COUNTRIES = {
    "us": ("United States", [("Emergency (Ambulance/Police/Fire)", "911"), ("Poison Control", "1-800-222-1222"), ("Suicide & Crisis Lifeline", "988")]),
    "ca": ("Canada", [("Emergency (Ambulance/Police/Fire)", "911")]),
    "gb": ("United Kingdom", [("Emergency (Ambulance/Police/Fire)", "999"), ("Emergency (alt.)", "112"), ("NHS non-emergency", "111")]),
    "ie": ("Ireland", [("Emergency", "112"), ("Emergency (alt.)", "999")]),
    "in": ("India", [("All-in-one Emergency", "112"), ("Ambulance", "102"), ("Ambulance (108 states)", "108")]),
    "bd": ("Bangladesh", [("National Emergency", "999")]),
    "ae": ("United Arab Emirates", [("Ambulance", "998"), ("Police", "999"), ("Fire", "997")]),
    "sa": ("Saudi Arabia", [("Ambulance", "997"), ("Police", "999"), ("Unified Emergency", "911")]),
    "tr": ("Türkiye", [("Emergency", "112")]),
    "eg": ("Egypt", [("Ambulance", "123"), ("Police", "122"), ("Fire", "180")]),
    "au": ("Australia", [("Emergency", "000"), ("Emergency (mobile)", "112")]),
    "nz": ("New Zealand", [("Emergency", "111")]),
    "cn": ("China", [("Ambulance", "120"), ("Police", "110"), ("Fire", "119")]),
    "jp": ("Japan", [("Ambulance / Fire", "119"), ("Police", "110")]),
    "za": ("South Africa", [("Ambulance", "10177"), ("Emergency (mobile)", "112"), ("Police", "10111")]),
    "ng": ("Nigeria", [("Emergency", "112"), ("Emergency (alt.)", "199")]),
    "de": ("Germany", [("Emergency / Ambulance / Fire", "112"), ("Police", "110")]),
    "fr": ("France", [("Ambulance (SAMU)", "15"), ("Emergency (EU)", "112"), ("Police", "17"), ("Fire", "18")]),
    "es": ("Spain", [("Emergency", "112")]),
    "it": ("Italy", [("Emergency", "112"), ("Ambulance", "118")]),
}
EU_112 = {"nl","be","at","se","no","dk","fi","pl","pt","gr","ch","cz","ro","hu","bg","hr","sk","si","lt","lv","ee","lu","mt","cy","is"}
FALLBACK = [("International emergency (works on most mobile networks)", "112")]


def country_options():
    """Name -> ISO code for the manual picker."""
    opts = {"Pakistan": "pk"}
    opts.update({v[0]: k for k, v in COUNTRIES.items()})
    return dict(sorted(opts.items()))


def helplines_for(country_code, region=""):
    cc = (country_code or "").lower()
    region = (region or "").lower()
    if cc == "pk":
        lines = PAKISTAN_DEFAULT
        for key, val in PAKISTAN.items():
            if key in region:
                lines = val
                break
        return {"country": "Pakistan", "region": region.title(), "numbers": lines, "exact": True}
    if cc in COUNTRIES:
        name, lines = COUNTRIES[cc]
        return {"country": name, "region": region.title(), "numbers": lines, "exact": True}
    if cc in EU_112:
        return {"country": cc.upper(), "region": "", "numbers": [("Emergency (EU-wide)", "112")], "exact": True}
    return {"country": cc.upper() if cc else "Unknown", "region": "", "numbers": FALLBACK, "exact": False}


def lookup_helplines(location):
    """Geocode a free-text location and return helplines, or None if it can't be resolved."""
    if not location or not location.strip():
        return None
    try:
        r = requests.get(URL, params={"q": location.strip(), "format": "json", "limit": 1, "addressdetails": 1},
                         headers=HEADERS, timeout=10)
        r.raise_for_status()
        rows = r.json()
        if not rows:
            return None
        addr = rows[0].get("address", {})
        region = addr.get("state") or addr.get("region") or addr.get("province") or ""
        city = addr.get("city") or addr.get("town") or addr.get("county") or location.strip()
        out = helplines_for(addr.get("country_code", ""), region)
        out["place"] = rows[0].get("display_name", location)
        out["city"] = city
        return out
    except Exception:
        return None
