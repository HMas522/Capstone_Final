"""
Purpose: Use Python to create a continuous intelligence and 
interactive analytics dashboard using Shiny for Python with 
interactive charts from Plotly Express.

Each Shiny app has two parts: 

- a user interface app_ui object (similar to the HTML in a web page) 
- a server function that provides the logic for the app (similar to JS in a web page).

"""
# First, import from the Python Standard Library (no installation required).
import asyncio

# Then, outside imports (these must be installed into your active Python environment).
from shiny import App, ui   # pip install shiny
import shinyswatch          # pip install shinyswatch

# Finally, import what we need from other local code files.

from util_logger import setup_logger

from dotenv import load_dotenv
import requests
import pandas as pd
from shiny import App, ui, render, reactive

load_dotenv()
def get_API_key():
    # Keep secrets in a .env file - load it, read the values.
    # Load environment variables from .env file
    load_dotenv()
    key = os.getenv("OPEN_FOOTBALL_API_KEY")
    return key

# Your API key from RapidAPI
API_KEY = "YOUR_RAPIDAPI_KEY"
API_HOST = "api-football-v1.p.rapidapi.com"
API_URL = "https://api-football-v1.p.rapidapi.com/v3/standings"

# Mapping leagues to their respective league IDs
LEAGUE_IDS = {
    "English Premier League": 39,
    "La Liga": 140,
    "Serie A": 135,
    "Bundesliga": 78,
    "Ligue 1": 61
}

# Fetch standings from the API
def get_standings(league_id):
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": API_HOST
    }
    params = {
        "league": league_id,
        "season": 2024  # Change the season if necessary
    }
    
    response = requests.get(API_URL, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        standings = data['response'][0]['league']['standings'][0]
        
        standings_list = []
        for team in standings:
            standings_list.append({
                "Rank": team['rank'],
                "Team": team['team']['name'],
                "Played": team['all']['played'],
                "Won": team['all']['win'],
                "Drawn": team['all']['draw'],
                "Lost": team['all']['lose'],
                "Points": team['points']
            })
        
        # Convert to a pandas DataFrame
        df = pd.DataFrame(standings_list)
        return df
    else:
        return None

# Shiny UI layout
app_ui = ui.page_fluid(
    ui.input_select("league", "Select League", choices=list(LEAGUE_IDS.keys())),
    ui.output_table("standings_table")
)

# Shiny Server logic
def server(input, output, session):
    
    @reactive.Calc
    def standings_df():
        league_id = LEAGUE_IDS[input.league()]
        return get_standings(league_id)
    
    @output()
    @render.render_table
    def standings_table():
        df = standings_df()
        if df is not None:
            return df
        else:
            return "Error fetching data from API"

# Create the app
app = App(app_ui, server)

# Run the app
if __name__ == "__main__":
    app.run()