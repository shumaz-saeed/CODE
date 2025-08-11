import os 
from langchain.agents import initialize_agent, AgentType
from langchain_core.tools import Tool
from langchain_core.language_models import LLM
from langchain_google_community import GooglePlacesTool
from typing import Optional, List, Any
import requests
from langchain_community.utilities.google_places_api import GooglePlacesAPIWrapper
from dotenv import load_dotenv

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
            return data["result"] 
        except KeyError:
            return str(data)  

    @property
    def _identifying_params(self) -> dict:
        return {"host": self.host}

    @property
    def _llm_type(self) -> str:
        return "rapidapi-chatgpt"
    
load_dotenv()

google_api_key = os.getenv("GOOGLE_MAPS_API_KEY")
llm = RapidAPIChatGPT(rapidapi_key=os.getenv("RAPID_API_KEY"))
location_tool = GooglePlacesTool( api_wrapper = google_api_key)

agent = initialize_agent(
    tools = location_tool,
    llm = llm,
    verbose = True,
    agent_type = AgentType.ZERO_SHOT_REACT_DESCRIPTION,
)

def find_nearby_places(location: str):

   def find_places(prompt: str)-> str:
       return agent.run(prompt)
   
