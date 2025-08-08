
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
from sqlalchemy import create_engine, text
from typing import List
import json

engine = create_engine(os.getenv("DATBASE_URL"))



def make_table(input_str: str) -> str:

    try:

        input_str = input_str.strip().lower()

        table_match = re.search(r"table called (\w+)|table named (\w+)|table (\w+)", input_str)
        if not table_match:
            return "Error: Could not find table name."
        table_name = next(g for g in table_match.groups() if g)

        col_match = re.search(r"columns (.+)", input_str)
        if not col_match:
            return "Error: Could not find column definitions."

        columns_raw = col_match.group(1)
        columns = []
        for col_def in columns_raw.split(","):
            parts = col_def.strip().split()
            if len(parts) < 2:
                return f"Error: Invalid column definition '{col_def.strip()}'"
            col_name = parts[0]
            col_type = " ".join(parts[1:])
            columns.append({"name": col_name, "type": col_type})

        column_defs = ", ".join([f"{col['name']} {col['type']}" for col in columns])
        sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({column_defs});"

        with engine.connect() as conn:
            conn.execute(text(sql))
            conn.commit()

        return f"✅ Table '{table_name}' created successfully with columns: {', '.join([col['name'] for col in columns])}"

    except Exception as e:
        return f"❌ Error: {str(e)}"



def get_tables(input_str: str = "") -> str:
    """
    Returns all tables in the public schema.
    Works even if the input is a natural language request.
    """
    try:
        if not re.search(r"(show|get|list|display).*(tables?)", input_str, re.IGNORECASE) and input_str.strip() != "":
            return "Unrecognized request for tables."

        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """))
            tables_present = [row[0] for row in result]

        if tables_present:
            return f"Tables found: {', '.join(tables_present)}"
        else:
            return "No tables found in the database."

    except Exception as e:
        return f"Error: {str(e)}"


tools =[ Tool(
    name="Weather Tool",
    func=get_current_weather,
    description="Get weather info by city name."
),
Tool(
    name = 'database_query',
    func=make_table,
    description = "Use this tool to make a new table in the postgres database."
),
Tool(
    name="List Tables Tool",
    func=get_tables,
    description="Use this to get a list of all table names in the PostgreSQL database."
)
]


agent = initialize_agent(
    tools =tools,
    llm = llm,
    agent_type = AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose = True
)
def get_response( input):
       response = agent.run(input)
       return response
