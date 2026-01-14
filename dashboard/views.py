import os
import requests
from django.shortcuts import render
from datetime import datetime

def get_state_generation(api_key, state_code):
    base_url = "https://api.eia.gov/v2/electricity/electric-power-operational-data/data"
    
    fuel_types = {
        'WND': 'Wind',
        'SUN': 'Solar',
        'NG': 'Natural Gas', 
        'COW': 'Coal',
        'NUC': 'Nuclear'
    }
    
    if not api_key:
        return None

    params = {
        'api_key': api_key,
        'frequency': 'annual',
        'data[0]': 'generation',
        'facets[location][]': state_code,
        'facets[sectorid][]': '99', 
        'facets[fueltypeid][]': list(fuel_types.keys()), 
        'sort[0][column]': 'period',
        'sort[0][direction]': 'asc',
    }
    
    try:

            
            processed = {}  
            
            for entry in raw_data:
                year = entry.get('period')
                fuel_code = entry.get('fueltypeid')
                try:
                    val = float(entry.get('generation', 0) or 0)
                except (ValueError, TypeError):
                    val = 0
                
                if year not in processed:
                    processed[year] = {k: 0 for k in fuel_types.values()}
                
                fuel_label = fuel_types.get(fuel_code)
                if fuel_label:
                    processed[year][fuel_label] += val 
            
            sorted_years = sorted(processed.keys())
            chart_data = {'years': sorted_years, 'datasets': []}
            
            colors = {
                'Wind': '#4bc0c0', 'Solar': '#ffcd56', 
                'Natural Gas': '#ff6384', 'Coal': '#36a2eb', 'Nuclear': '#9966ff'
            }
            
            for fuel in fuel_types.values():
                data_series = [processed[y].get(fuel, 0) for y in sorted_years]
                chart_data['datasets'].append({
                    'label': fuel,
                    'data': data_series,
                    'borderColor': colors.get(fuel, '#ccc'),
                    'backgroundColor': colors.get(fuel, '#ccc')
                })
            return chart_data
    except Exception as e:
        print(f"State Data Error: {e}")
        return None
    return None

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

def state_analysis(request):
    api_key = os.getenv('EIA_API_KEY')
    selected_state = request.GET.get('state', 'TX')
    state_chart_data = get_state_generation(api_key, selected_state)
    
    all_states = [
        'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 
        'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 
        'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 
        'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 
        'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'
    ]

    context = {
        'state_data': state_chart_data,
        'selected_state': selected_state,
        'all_states': all_states,
    }
    return render(request, 'dashboard/state_analysis.html', context)

