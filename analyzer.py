import math

def analyze_security(auth, cipher):
    security = "Unknown"
    score = 0
    
    # Analyze based on netsh string outputs
    auth = auth.lower()
    cipher = cipher.lower()
    
    if "open" in auth:
        security = "Open"
        score = 10
    elif "wep" in auth or "wep" in cipher:
        security = "WEP"
        score = 30
    elif "wpa3" in auth:
        if "enterprise" in auth:
            security = "WPA3-Enterprise"
            score = 100
        else:
            security = "WPA3-Personal"
            score = 95
    elif "wpa2" in auth:
        if "enterprise" in auth:
            security = "WPA2-Enterprise"
            score = 90
        else:
            security = f"WPA2-Personal ({cipher.upper()})"
            score = 80
    elif "wpa" in auth:
        security = f"WPA-Personal ({cipher.upper()})"
        score = 50
    else:
        # Fallback
        if cipher == "ccmp":
            security = "WPA2"
            score = 80
        elif cipher == "tkip":
            security = "WPA"
            score = 50
            
    return security, score

def estimate_distance(freq_mhz, signal_dbm):
    # Free-Space Path Loss (FSPL) estimation
    # Distance (m) = 10 ^ ((27.55 - (20 * log10(freq)) + abs(signal_dbm)) / 20)
    try:
        if freq_mhz <= 0:
            return 0.0
        exp = (27.55 - (20 * math.log10(freq_mhz)) + abs(signal_dbm)) / 20.0
        distance = math.pow(10.0, exp)
        return round(distance, 2)
    except Exception:
        return 0.0

def analyze_networks(parsed_results):
    analyzed = []
    
    security_counts = {}
    
    for net in parsed_results:
        sec_type, score = analyze_security(net['auth'], net['cipher'])
        
        if sec_type in security_counts:
            security_counts[sec_type] += 1
        else:
            security_counts[sec_type] = 1
            
        net['security'] = sec_type
        net['score'] = score
        net['distance'] = estimate_distance(net['freq'], net['signal'])
        
        analyzed.append(net)
        
    return analyzed, security_counts

def get_channel_recommendation(analyzed_networks):
    channels_24 = {i: 0 for i in range(1, 15)}
    channels_5 = {} # Dynamic for 5GHz
    
    for net in analyzed_networks:
        ch = net['channel']
        band = net.get('band', '')
        
        if '2.4' in band or (1 <= ch <= 14):
            channels_24[ch] += 1
        elif '5' in band or ch >= 36:
            if ch not in channels_5:
                channels_5[ch] = 0
            channels_5[ch] += 1
            
    # Find least crowded channel 2.4GHz (1, 6, 11 are non-overlapping in most regions)
    rec_24 = 1
    min_count_24 = float('inf')
    for ch in [1, 6, 11]:
        if channels_24[ch] < min_count_24:
            min_count_24 = channels_24[ch]
            rec_24 = ch
            
    # Find least crowded channel 5GHz
    rec_5 = None
    if channels_5:
        # Common 5GHz non-DFS channels: 36, 40, 44, 48, 149, 153, 157, 161
        common_5g = [36, 40, 44, 48, 149, 153, 157, 161]
        min_count_5 = float('inf')
        for ch in common_5g:
            count = channels_5.get(ch, 0)
            if count < min_count_5:
                min_count_5 = count
                rec_5 = ch
                
    return {'2.4GHz': rec_24, '5GHz': rec_5}, {'2.4GHz': channels_24, '5GHz': channels_5}
