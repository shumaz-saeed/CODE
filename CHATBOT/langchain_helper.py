
import os
import psycopg2
import requests
from langchain.agents import initialize_agent
from langchain.agents import AgentType
from langchain_core.tools import Tool
from langchain_openai import ChatOpenAI
import operator
from dotenv import load_dotenv
load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
weather_api_key = os.getenv("OPENWEATHERMAP_API_KEY")
endpoint = "https://models.github.ai/inference"

model_name = "openai/gpt-4o-mini"

llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0.5, api_key=openai_api_key)

def get_current_weather(city: str) -> str:
    
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": weather_api_key,
        "units": "metric"
    }
    
    try:
        response = requests.get(base_url, params=params)
        data = response.json()
        if data['cod'] != 200:
            return f'error occured' 
        elif data["cod"] == 200:
            weather_desc = data["weather"][0]["description"]
            temperature = data["main"]["temp"]
            return f"The current weather in {city} is {weather_desc} with a temperature of {temperature}°C."
    except Exception as e:
        return "could not fetch weather data. Please try again later." + str(e)
