import json
import requests
import math

def to_dollar_yearly(amount, currency, periodicity):
    amount2 = amount

    if not currency == 'USD':
        params = { 'access_key': 'd5568af226a6405cf3f461404b5ca961', 'symbols': 'USD,{}'.format(currency), 'format': '1' }
        url = "http://data.fixer.io/api/latest"
        r = requests.get(url,params=params).json()

        if r['success'] == True:
            usd = r['rates']['USD']
            other = r['rates'][currency]
            amount2 = usd*amount/other

    if not periodicity == 'yearly':
        if periodicity == 'monthly':
            amount2 = amount2*12

        if periodicity == 'hourly':
            amount2 = amount2*8*22*12   # Aprox, changes with country

    return amount2



def languaje_fluency(fluency):
    fluency_num = 0
    if fluency == 'reading':
        fluency_num = 1
    if fluency == 'conversational':
        fluency_num = 2
    if fluency == 'fully-fluent':
        fluency_num = 3

    return fluency_num



def asign_values(opportunities,oppo_type):
    for a in opportunities:
        if a['interest'] == oppo_type:
            if a['field'] == 'desirable-compensation-currency':
                oppo_currency   = a['data'][0:3]
            if a['field'] == 'desirable-compensation-amount':
                oppo_amount     = a['data']
            if a['field'] == 'desirable-compensation-periodicity':
                oppo_period     = a['data']

    return oppo_currency, oppo_amount, oppo_period



def get_distance(lat1, lat2, lon1, lon2):
    
    R = 6378.137 # Radius of earth in KM
    d_lat = lat2 * math.pi / 180 - lat1 * math.pi / 180
    d_lon = lon2 * math.pi / 180 - lon1 * math.pi / 180
    a = math.sin(d_lat/2) * math.sin(d_lat/2) + math.cos(lat1 * math.pi / 180) * math.cos(lat2 * math.pi / 180) * math.sin(d_lon/2) * math.sin(d_lon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = R * c  # Kilometers

    return d