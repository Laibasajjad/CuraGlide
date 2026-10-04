EMERGENCY_KEYWORDS = ['severe chest pain','difficulty breathing','cannot breathe','passed out','unconscious','severe bleeding','one-sided weakness','face drooping','seizure']

def quick_safety_check(text):
    t = (text or '').lower()
    hits = [x for x in EMERGENCY_KEYWORDS if x in t]
    if hits:
        return {'level':'URGENT ATTENTION','message':'Some symptoms described may need urgent medical evaluation. If symptoms are severe, sudden, worsening, or you feel unsafe, seek emergency help now.','hits':hits}
    return {'level':'GENERAL','message':'This tool provides health information only and cannot confirm a diagnosis. Seek professional care if symptoms are severe, worsening, or concerning.','hits':[]}
