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

            
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        payload = response.json()
        
        if 'response' in payload and 'data' in payload['response']:
            raw_data = payload['response']['data']
            
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

def get_net_load_data(api_key, region_code):
    # Endpoints
    url_demand = "https://api.eia.gov/v2/electricity/rto/region-data/data"
    url_fuel = "https://api.eia.gov/v2/electricity/rto/fuel-type-data/data"
    
    if not api_key:
        return None

    # 1. Fetch Gross Demand
    params_demand = {
        'api_key': api_key,
        'frequency': 'local-hourly',
        'data[0]': 'value',
        'facets[respondent][]': region_code,
        'sort[0][column]': 'period',
        'sort[0][direction]': 'desc',
        'length': 48 # Last 48 hours for a good curve
    }
    
    try:
        r_demand = requests.get(url_demand, params=params_demand)
        r_demand.raise_for_status()
        demand_data = r_demand.json().get('response', {}).get('data', [])
    except Exception as e:
        print(f"Net Load Demand Error: {e}")
        return None

    # 2. Fetch Renewables (Wind + Solar)
    params_fuel = {
        'api_key': api_key,
        'frequency': 'local-hourly',
        'data[0]': 'value',
        'facets[respondent][]': region_code,
        'facets[fueltype][]': ['WND', 'SUN'],
        'sort[0][column]': 'period',
        'sort[0][direction]': 'desc',
        'length': 100 # Fetch more to ensure we cover the same time range for both fuels
    }
    
    try:
        r_fuel = requests.get(url_fuel, params=params_fuel)
        r_fuel.raise_for_status()
        fuel_data = r_fuel.json().get('response', {}).get('data', [])
    except Exception as e:
        print(f"Net Load Fuel Error: {e}")
        return None

    # 3. Process & Align Data
    # Map: 'YYYY-MM-DDTHH' -> {'demand': X, 'wind': Y, 'solar': Z}
    combined = {}
    
    # Process Demand
    for d in demand_data:
        p = d.get('period')
        if p not in combined: combined[p] = {'demand': 0, 'solar': 0, 'wind': 0}
        combined[p]['demand'] = float(d.get('value', 0) or 0)
        combined[p]['ts'] = d.get('period') # Keep timestamp for sorting

    # Process Renewables
    for f in fuel_data:
        p = f.get('period')
        ft = f.get('fueltype')
        val = float(f.get('value', 0) or 0)
        
        if p in combined:
            if ft == 'SUN': combined[p]['solar'] += val
            if ft == 'WND': combined[p]['wind'] += val

    # Validate we have complete data points (demand + at least one fuel potentially)
    # Sort by time ascending
    sorted_periods = sorted(combined.keys())
    
    labels = []
    dataset_demand = []
    dataset_net = []
    dataset_solar = []
    dataset_wind = []
    
    for p in sorted_periods:
        data = combined[p]
        # Clean label (remove date if redundant, but keep for now)
        label = p.split('T')[1] + ":00" if 'T' in p else p
        
        demand = data['demand']
        solar = data['solar']
        wind = data['wind']
        net_load = demand - (solar + wind)
        
        labels.append(label)
        dataset_demand.append(demand)
        dataset_net.append(net_load)
        dataset_solar.append(solar)
        dataset_wind.append(wind)

    return {
        'labels': labels,
        'gross_demand': dataset_demand,
        'net_load': dataset_net,
        'solar': dataset_solar,
        'wind': dataset_wind
    }

def net_load_analysis(request):
    api_key = os.getenv('EIA_API_KEY')
    selected_region = request.GET.get('region', 'CISO') # Default to CAISO (California)
    
    # Region Map
    regions = {
        'CISO': 'CAISO (California)',
        'ERCO': 'ERCOT (Texas)',
        'PJM': 'PJM (East/Mid-Atlantic)',
        'MISO': 'MISO (Midwest)',
        'NYIS': 'NYISO (New York)',
        'ISNE': 'ISO-NE (New England)'
    }
    
    chart_data = get_net_load_data(api_key, selected_region)
    
    context = {
        'chart_data': chart_data,
        'selected_region': selected_region,
        'selected_region_name': regions.get(selected_region, selected_region),
        'all_regions': regions,
    }
    return render(request, 'dashboard/net_load.html', context)

