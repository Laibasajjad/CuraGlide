import math, requests
URL='https://nominatim.openstreetmap.org/search'
HEADERS={'User-Agent':'CuraGlide/1.0'}

def calculate_distance(lat1,lon1,lat2,lon2):
    r=6371.0
    p1,p2=math.radians(float(lat1)),math.radians(float(lat2))
    dp=math.radians(float(lat2)-float(lat1)); dl=math.radians(float(lon2)-float(lon1))
    a=math.sin(dp/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return r*2*math.atan2(math.sqrt(a),math.sqrt(1-a))

def geocode_location(location):
    if not location or not location.strip(): return None
    try:
        r=requests.get(URL,params={'q':location.strip(),'format':'json','limit':1,'addressdetails':1},headers=HEADERS,timeout=10); r.raise_for_status(); rows=r.json()
        if not rows:return None
        x=rows[0]; return {'latitude':float(x['lat']),'longitude':float(x['lon']),'display_name':x.get('display_name',location)}
    except Exception:return None

def find_hospitals(location):
    origin=geocode_location(location)
    if not origin:return {'success':False,'error':'Could not find that location. Try a city or area name.','hospitals':[]}
    lat,lon=origin['latitude'],origin['longitude']; dlat=25/111; dlon=25/(111*max(math.cos(math.radians(lat)),.1))
    params={'q':'hospital','format':'json','limit':15,'addressdetails':1,'bounded':1,'viewbox':f'{lon-dlon},{lat+dlat},{lon+dlon},{lat-dlat}'}
    try:
        r=requests.get(URL,params=params,headers=HEADERS,timeout=15); r.raise_for_status(); out=[]
        for x in r.json():
            try:
                hlat,hlon=float(x['lat']),float(x['lon']); dist=calculate_distance(lat,lon,hlat,hlon)
                if dist<=25: out.append({'name':x.get('display_name','Unknown hospital').split(',')[0],'address':x.get('display_name','Address unavailable'),'distance':f'{dist:.1f} km','latitude':hlat,'longitude':hlon})
            except Exception: pass
        out.sort(key=lambda x:float(x['distance'].split()[0]))
        return {'success':True,'origin':origin,'hospitals':out[:10]}
    except Exception as e:return {'success':False,'error':f'Hospital search failed: {e}','hospitals':[]}
