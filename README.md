US Electricity Market Analysis & Prediction Dashboard
This project is a comprehensive data analysis and predictive modeling tool for the U.S. electricity market. It uses a synthetic 20-year dataset to analyze historical trends and forecast future electricity prices and sales for the next five years on a state-by-state basis.

The final output is a fully interactive, single-page web dashboard that visualizes both the historical data and the machine learning predictions.

Dashboard Preview
Below are images of the interactive dashboard, showing the forecasts for a sample state.
<img width="1228" height="757" alt="image" src="https://github.com/user-attachments/assets/6f137b77-64dc-4d7a-b758-d60a01206ae4" />
<img width="1065" height="594" alt="image" src="https://github.com/user-attachments/assets/c38939a4-9453-4347-9e27-10d3d99c7a70" />


Price Forecast Chart
Shows the historical price trend in blue and the 5-year machine learning forecast in orange.
<img width="1228" height="757" alt="image" src="https://github.com/user-attachments/assets/b9cddc3f-fa3c-4605-a7b7-57f6703fb887" />

Sales Forecast Chart
Shows the historical sales trend in green and the 5-year machine learning forecast in red.
<img width="1065" height="594" alt="image" src="https://github.com/user-attachments/assets/e81f0937-214e-461d-8d47-a444b087852d" />


Features
Interactive Dashboard: A clean, user-friendly web interface built with Plotly.js.

State-Level Analysis: Users can select any state from a dropdown menu to view specific data and forecasts.

Dual Forecasting: The dashboard displays two separate charts:

Price Forecast: Shows the historical average price (cents/kWh) and a 5-year prediction.

Sales Forecast: Shows the historical total sales (MWh) and a 5-year prediction.

Predictive Modeling: Uses a Linear Regression model from Scikit-learn trained on 20 years of historical data for each state.

Dynamic Data Generation: The core Python script can generate the entire 20-year dataset from scratch, making the project fully reproducible.

How It Works
This project consists of two main components:

The Python Analysis & Generation Script (analysis_server.py)
This script is the engine of the project. It performs all the heavy lifting:

Generates a 20-year synthetic dataset using Pandas and NumPy.

Trains a unique LinearRegression model for each of the 50 states to predict future prices and sales.

Bundles all the historical data and predictions into a single, self-contained HTML file (prediction_dashboard.html).

The Interactive HTML Dashboard (prediction_dashboard.html)
This is the final product. It is a single HTML file with no external dependencies besides Plotly.js (loaded from a CDN).

All the historical and predicted data is embedded directly into the file as a JSON object.

JavaScript is used to handle user interactions (like selecting a state) and dynamically update the Plotly charts.

How to Run This Project Locally
Prerequisites: Ensure you have Python 3 and the following libraries installed:

pip install pandas scikit-learn plotly

Run the Script: Navigate to the project directory in your terminal and run the main Python script.

python analysis_server.py
