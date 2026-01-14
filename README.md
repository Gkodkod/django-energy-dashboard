# Django Energy Dashboard

A comprehensive energy visualization dashboard built with **Django** and **Chart.js**. This application fetches real-time and historical data from the **U.S. Energy Information Administration (EIA) API** to visualize the US electricity grid's demand and generation trends.

## Features

-   **Real-Time US Demand:** Visualizes the electricity demand (MWh) for the Lower 48 states over the last 24 hours.
-   **State Analysis:** Interactive tool to explore historical annual electricity generation trends by fuel type for any US state.
-   **Net Load & Duck Curve Analysis:** Advanced visualization showing the impact of solar and wind on grid demand. Track the "Duck Curve" and ramp rates across major regions like CAISO, ERCOT, and PJM.
-   **Congestion Proxy:** A unique tool that proxies "Grid Congestion" by comparing real-time Regional Demand against the Annual Nameplate Capacity of its representative state (e.g., ERCOT vs. Texas). Features a Demand/Capacity chart and an hourly utilization heatmap.
-   **Dark Mode UI:** A premium, responsive dark-themed interface built with custom CSS.
-   **Secure Configuration:** API keys are managed safely via environment variables.

## Technology Stack

-   **Backend:** Python 3, Django 6.0.1
-   **Data Source:** U.S. EIA Open Data API (v2)
-   **Frontend:** Django Templates, HTML5, CSS3, Chart.js
-   **Utilities:** `requests` for API fetching, `python-dotenv` for configuration.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Gkodkod/django-energy-dashboard.git
    cd django-energy-dashboard
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    # Windows
    .\venv\Scripts\activate
    # Mac/Linux
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install django requests python-dotenv
    ```

4.  **Set up Environment Variables:**
    Create a `.env` file in the root directory (copy from `.env.example` if available) and add your EIA API Key:
    ```env
    EIA_API_KEY=your_api_key_here
    DEBUG=True
    SECRET_KEY=your_secret_key
    ```
    *Note: You can get a free API key from the [EIA Open Data website](https://www.eia.gov/opendata/).*

5.  **Run Migrations:**
    ```bash
    python manage.py migrate
    ```

6.  **Start the Server:**
    ```bash
    python manage.py runserver
    ```

7.  **View the Dashboard:**
    Open your browser to `http://127.0.0.1:8000`.

## License

MIT License.
