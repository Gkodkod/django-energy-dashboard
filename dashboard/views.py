import os
import requests
from django.shortcuts import render
from datetime import datetime

def index(request):
    api_key = os.getenv('EIA_API_KEY')
    
    # --- 1. Real-time US Demand ---
    demand_context = {'labels': [], 'data': []}
    error_msg = None
    
    try:
        # Fetch last 24 records of US Hourly Demand
        base_url_rto = "https://api.eia.gov/v2/electricity/rto/region-data/data"
        params_rto = {
            'api_key': api_key,
            'frequency': 'local-hourly',
            'data[0]': 'value',
            'facets[respondent][]': 'US48',
            'sort[0][column]': 'period',
            'sort[0][direction]': 'desc',
            'length': 24
        }
        res_rto = requests.get(base_url_rto, params=params_rto)
        res_rto.raise_for_status()
        
        json_resp = res_rto.json()
        if 'response' in json_resp and 'data' in json_resp['response']:
             data_rto = json_resp['response']['data']
             data_rto.reverse()
             for entry in data_rto:
                p_str = entry.get('period', '')
                label = p_str.split('T')[1] + ":00" if 'T' in p_str else p_str
                demand_context['labels'].append(label)
                demand_context['data'].append(entry.get('value', 0))
        else:
            error_msg = "API response format unexpected."
            
    except Exception as e:
        error_msg = f"US Demand Data unavailable: {str(e)}"
        
    context = {
        'labels': demand_context['labels'],
        'data': demand_context['data'],
        'error': error_msg
    }

    return render(request, 'dashboard/index.html', context)

