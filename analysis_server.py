# --- Final Python Code for Analysis, Prediction, and Dashboard Serving ---
# This script is now self-contained and performs several tasks:
# 1. Generates a synthetic 20-year electricity dataset internally in memory.
# 2. Analyzes the data and trains a linear regression model to predict prices and sales.
# 3. Automatically generates a new, interactive HTML dashboard file with all data and predictions.
# 4. Starts a quiet local web server in the background to host the new HTML dashboard.

import pandas as pd
import plotly.graph_objects as go
import http.server
import socketserver
import webbrowser
import os
import sys
import time
import traceback
import threading
import socket
import numpy as np
import json
from sklearn.linear_model import LinearRegression

# --- Function to generate and return a DataFrame ---
def generate_synthetic_dataframe():
    """Generates a realistic 20-year dataset and returns it as a DataFrame."""
    print("Generating synthetic data in memory...")
    states = [
        'Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado', 'Connecticut', 'Delaware', 'Florida', 
        'Georgia', 'Hawaii', 'Idaho', 'Illinois', 'Indiana', 'Iowa', 'Kansas', 'Kentucky', 'Louisiana', 'Maine', 
        'Maryland', 'Massachusetts', 'Michigan', 'Minnesota', 'Mississippi', 'Missouri', 'Montana', 'Nebraska', 
        'Nevada', 'New Hampshire', 'New Jersey', 'New Mexico', 'New York', 'North Carolina', 'North Dakota', 'Ohio', 
        'Oklahoma', 'Oregon', 'Pennsylvania', 'Rhode Island', 'South Carolina', 'South Dakota', 'Tennessee', 
        'Texas', 'Utah', 'Vermont', 'Virginia', 'Washington', 'West Virginia', 'Wisconsin', 'Wyoming'
    ]
    sectors = ['Residential', 'Commercial', 'Industrial']
    years = range(2005, 2025)
    
    data = []
    for year in years:
        for state in states:
            for sector in sectors:
                base_price = 6 + (year - 2005) * 0.4 + (hash(state) % 100) / 50.0
                price_noise = np.random.normal(0, 0.5)
                price = base_price + price_noise
                base_sales = 10000 + (year - 2005) * 500
                if sector == 'Industrial': base_sales *= 1.5
                elif sector == 'Commercial': base_sales *= 1.2
                sales_noise = np.random.normal(0, 1000)
                sales = base_sales + sales_noise
                data.append({
                    'Year': year, 'State': state, 'Sector': sector,
                    'Price (cents/kWh)': round(price, 2), 'Sales (MWh)': int(sales)
                })

    df = pd.DataFrame(data)
    print("Synthetic data successfully generated.")
    return df

# --- NEW: Function to create the interactive HTML dashboard ---
def create_prediction_dashboard_html(historical_df, predictions, future_years, filename="prediction_dashboard.html"):
    """Generates a self-contained HTML file with interactive Plotly charts."""
    print(f"\n--- Step 3: Generating new HTML dashboard file ---")
    
    # Consolidate all data into a JSON-serializable format
    dashboard_data = {
        'states': sorted(historical_df['State'].unique()),
        'future_years': future_years.flatten().tolist(),
        'historical': {},
        'predictions': predictions
    }
    
    # Prepare historical data for each state
    for state in dashboard_data['states']:
        state_df = historical_df[historical_df['State'] == state]
        yearly_data = state_df.groupby('Year').agg({
            'Price (cents/kWh)': 'mean',
            'Sales (MWh)': 'sum'
        }).reset_index()
        dashboard_data['historical'][state] = yearly_data.to_dict(orient='list')

    # Convert the consolidated data to a JSON string
    data_json = json.dumps(dashboard_data)

    html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>UPDATED Prediction Dashboard</title>
        <script src="https://cdn.plot.ly/plotly-2.24.1.min.js"></script>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; margin: 0; background-color: #f8f9fa; }}
            .container {{ padding: 20px; }}
            h1 {{ text-align: center; color: #333; }}
            .controls {{ display: flex; justify-content: center; align-items: center; margin-bottom: 20px; }}
            label {{ font-size: 1.1em; margin-right: 10px; }}
            select {{ padding: 8px; font-size: 1em; border-radius: 5px; border: 1px solid #ccc; }}
            .chart-container {{ display: flex; flex-wrap: wrap; justify-content: center; gap: 20px; }}
            .chart {{ width: 100%; max-width: 800px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); background: white; border-radius: 8px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Electricity Market Prediction Dashboard (20-Year Data)</h1>
            <div class="controls">
                <label for="state-selector">Select State:</label>
                <select id="state-selector"></select>
            </div>
            <div class="chart-container">
                <div id="price-chart" class="chart"></div>
                <div id="sales-chart" class="chart"></div>
            </div>
        </div>

        <script>
            const data = {data_json};
            const stateSelector = document.getElementById('state-selector');

            function populateSelector() {{
                data.states.forEach(state => {{
                    const option = document.createElement('option');
                    option.value = state;
                    option.textContent = state;
                    stateSelector.appendChild(option);
                }});
                stateSelector.value = 'California'; // Default state
            }}

            function updateCharts() {{
                const selectedState = stateSelector.value;
                const historical = data.historical[selectedState];
                const prediction = data.predictions[selectedState];
                const futureYears = data.future_years;

                const priceTraceHist = {{ x: historical.Year, y: historical['Price (cents/kWh)'], mode: 'lines+markers', name: 'Historical Price', line: {{ color: '#1f77b4' }} }};
                const priceTracePred = {{ x: futureYears, y: prediction.prices, mode: 'lines+markers', name: 'Predicted Price', line: {{ color: '#ff7f0e', dash: 'dash' }} }};
                const priceLayout = {{ 
                    title: `<b>Price Forecast for ${{selectedState}}</b>`, 
                    xaxis: {{ title: 'Year' }}, 
                    yaxis: {{ title: 'Average Price (cents/kWh)' }}, 
                    margin: {{ t: 50, l: 60, r: 30, b: 50 }}, 
                    legend: {{ x: 0.01, y: 0.99, yanchor: 'top', bgcolor: 'rgba(255, 255, 255, 0.8)', bordercolor: '#ccc', borderwidth: 1 }} 
                }};
                Plotly.newPlot('price-chart', [priceTraceHist, priceTracePred], priceLayout);

                const salesTraceHist = {{ x: historical.Year, y: historical['Sales (MWh)'], mode: 'lines+markers', name: 'Historical Sales', line: {{ color: '#2ca02c' }} }};
                const salesTracePred = {{ x: futureYears, y: prediction.sales, mode: 'lines+markers', name: 'Predicted Sales', line: {{ color: '#d62728', dash: 'dash' }} }};
                const salesLayout = {{ 
                    title: `<b>Sales Forecast for ${{selectedState}}</b>`, 
                    xaxis: {{ title: 'Year' }}, 
                    yaxis: {{ title: 'Total Sales (MWh)' }}, 
                    margin: {{ t: 50, l: 60, r: 30, b: 50 }}, 
                    legend: {{ x: 0.01, y: 0.99, yanchor: 'top', bgcolor: 'rgba(255, 255, 255, 0.8)', bordercolor: '#ccc', borderwidth: 1 }} 
                }};
                Plotly.newPlot('sales-chart', [salesTraceHist, salesTracePred], salesLayout);
            }}

            populateSelector();
            updateCharts();
            stateSelector.addEventListener('change', updateCharts);
        </script>
    </body>
    </html>
    """
    
    with open(filename, 'w') as f:
        f.write(html_template)
    print(f"HTML dashboard generated successfully at: {os.path.abspath(filename)}")


# --- Main script execution starts here ---

# Part 1: Data Generation and Analysis
print("\n--- Step 1: Generating and Analyzing Data ---")
df_filtered = None
try:
    df = generate_synthetic_dataframe()
    df['YearDT'] = pd.to_datetime(df['Year'], format='%Y')
    df_filtered = df.copy()
    print("Data loaded and cleaned successfully.")
except Exception:
    print(f"\n[ERROR] An unexpected error occurred during data analysis:")
    traceback.print_exc()
    df_filtered = None

# Part 2: Prediction Modeling
predictions = {}
future_years_np = np.array([])
if df_filtered is not None:
    print("\n--- Step 2: Predicting Future Prices and Sales ---")
    # FIX: Corrected the typo from --1 to -1
    future_years_np = np.array(range(2025, 2030)).reshape(-1, 1)
    all_states = df_filtered['State'].unique()
    
    for state in all_states:
        state_df = df_filtered[df_filtered['State'] == state]
        yearly_data = state_df.groupby('Year').agg({
            'Price (cents/kWh)': 'mean', 'Sales (MWh)': 'sum'
        }).reset_index()
        X = yearly_data[['Year']]
        price_model = LinearRegression().fit(X, yearly_data['Price (cents/kWh)'])
        sales_model = LinearRegression().fit(X, yearly_data['Sales (MWh)'])
        predictions[state] = {
            'prices': price_model.predict(future_years_np).tolist(),
            'sales': sales_model.predict(future_years_np).tolist()
        }
    print("Prediction models trained for all states.")

# Part 3: Dashboard Generation and Server Launch
if df_filtered is not None:
    HTML_FILE = "prediction_dashboard.html"
    create_prediction_dashboard_html(df_filtered, predictions, future_years_np, HTML_FILE)

    def find_free_port(start_port=8000):
        port = start_port
        while True:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                if s.connect_ex(('localhost', port)) != 0: return port
            port += 1
            
    class QuietHandler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, format, *args): return
        
    def run_server(port):
        socketserver.TCPServer.allow_reuse_address = True
        with socketserver.TCPServer(("", port), QuietHandler) as httpd:
            httpd.serve_forever()

    print("\n--- Step 4: Starting background web server ---")
    PORT = find_free_port()
    server_thread = threading.Thread(target=run_server, args=(PORT,))
    server_thread.daemon = True
    server_thread.start()
    print(f"Server thread started successfully on port {PORT}.")
    time.sleep(1)

    try:
        print("\n--- Step 5: Opening the new interactive dashboard ---")
        webbrowser.open_new_tab(f"http://localhost:{PORT}/{HTML_FILE}")
        print("\n--- SCRIPT COMPLETE ---")
        print(f"The web server is running in the background at http://localhost:{PORT}")
        input("Press Enter in this terminal to stop the server and exit the script.")

    except Exception:
        print(f"\n[ERROR] An unexpected error occurred while opening the dashboard:")
        traceback.print_exc()
else:
    print("\n--- Script Finished ---")
    print("The script was not completed due to an error during the data analysis phase.")

