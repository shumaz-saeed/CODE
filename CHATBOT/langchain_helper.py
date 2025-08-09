
import os
import re
import psycopg2
import requests
from langchain.agents import initialize_agent
from langchain.agents import AgentType
from langchain_core.tools import Tool
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text
from typing import List
import json

load_dotenv()


from langchain_core.language_models import LLM
from typing import Optional, List, Any
import requests

class RapidAPIChatGPT(LLM):
    rapidapi_key: str
    host: str = "open-ai21.p.rapidapi.com"
    url: str = "https://open-ai21.p.rapidapi.com/chatgpt"

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        payload = {
            "messages": [{"role": "user", "content": prompt}],
            "web_access": False
        }
        headers = {
            "x-rapidapi-key": os.getenv("RAPID_API_KEY"),
            "x-rapidapi-host":  os.getenv("RAPID_API_HOST"),
            "Content-Type": "application/json"
        }

        response = requests.post(self.url, json=payload, headers=headers)
        data = response.json()

        try:
            return data["result"]  # The main text output from API
        except KeyError:
            return str(data)  # In case API returns unexpected format

    @property
    def _identifying_params(self) -> dict:
        return {"host": self.host}

    @property
    def _llm_type(self) -> str:
        return "rapidapi-chatgpt"
weather_api_key = os.getenv("OPENWEATHERMAP_API_KEY")


llm = RapidAPIChatGPT(rapidapi_key="YOUR_RAPIDAPI_KEY_HERE")







## these are the functions called in the tools



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

        return f" Table '{table_name}' created successfully with columns: {', '.join([col['name'] for col in columns])}"

    except Exception as e:
        return f" Error: {str(e)}"



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




def get_data(input_str: str) -> str:
    """
    Fetches data for a person by name from all relevant tables.
    The input should be the person's name.
    """
    try:
        person_name = input_str.strip()

        all_tables_str = get_tables("list tables")
        if all_tables_str.startswith("Error"):
            return all_tables_str
        
        table_names = [name.strip() for name in all_tables_str.replace("Tables found:", "").split(',') if name.strip()]
        
        results = {}
        for table in table_names:
            with engine.connect() as conn:
                inspector = inspect(engine)
                columns = inspector.get_columns(table)
                column_names = [col['name'] for col in columns]
                
                if 'name' in column_names:
                    query = text(f"SELECT * FROM {table} WHERE name = :name")
                    result = conn.execute(query, {"name": person_name}).fetchall()
                    if result:
                        results[table] = [row._asdict() for row in result]
        
        if results:
            return json.dumps(results, indent=2)
        else:
            return "No matching records found for that name in any table."
    except Exception as e:
        return f"Error fetching data: {e}"


def delete_table(input_str: str) -> str:
    """Delete a table from the database, even if input is natural language."""
    try:
        match = re.search(r"(?:delete|drop|remove)\s+table?\s*([a-zA-Z_][a-zA-Z0-9_]*)", input_str, re.IGNORECASE)
        
        if not match:
            return "Error: Could not find table name to delete."

        table_name = match.group(1)

        with engine.connect() as conn:
            conn.execute(text(f"DROP TABLE IF EXISTS {table_name}"))
            conn.commit()

        return f"Table '{table_name}' deleted successfully."

    except Exception as e:
        return f"Error deleting table: {e}"
      






tools =[
Tool(
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
),
Tool(
    name="get_info",
    func=get_data,
    description='Use this tool to find information about a person by their name. It searches all relevant tables in the database. The input should be just the person\'s name, e.g., "Ali".'
),
Tool(
    name = 'delete_table',
    func = get_tables,
    description = 'use this tool to delete a table from the database by the name of the table.'
)
]


## this is the agent
agent = initialize_agent(
    tools =tools,
    llm = llm,
    agent_type = AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose = True,
    handle_parsing_errors= True # This will handle parsing errors gracefully
)


## and this is the function to call the agent and get respond
def get_response( input_str: str) -> str:
       response = agent.run(input_str)
       return response


