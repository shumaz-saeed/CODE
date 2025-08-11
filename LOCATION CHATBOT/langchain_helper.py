import os
import logging
import requests
from typing import Optional, List
from dotenv import load_dotenv
from langchain.agents import initialize_agent, AgentType
from langchain_core.tools import Tool
from langchain_core.language_models import LLM
from langchain_google_community import GooglePlacesTool
from langchain_community.utilities.google_places_api import GooglePlacesAPIWrapper

# ==========================
# Logging Configuration
# ==========================
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)

# ==========================
# Custom RapidAPI ChatGPT LLM
# ==========================
class RapidAPIConversationLLaMA(LLM):
    rapidapi_key: str
    host: str = "open-ai21.p.rapidapi.com"
    url: str = "https://open-ai21.p.rapidapi.com/conversationllama"

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        logger.debug(f"LLM received prompt: {prompt}")

        payload = {
            "messages": [{"role": "user", "content": prompt}],
            "web_access": False
        }
        headers = {
            "x-rapidapi-key": os.getenv("RAPID_API_KEY", "318051118dmsh0426f1b30cb5048p155216jsn075da5396396"),
            "x-rapidapi-host": os.getenv("RAPID_API_HOST", self.host),
            "Content-Type": "application/json"
        }

        logger.debug(f"Sending request to RapidAPI ConversationLLaMA endpoint: {self.url}")
        logger.debug(f"Headers: {headers}")
        logger.debug(f"Payload: {payload}")

        response = requests.post(self.url, json=payload, headers=headers)
        logger.debug(f"RapidAPI raw response: {response.text}")

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
        return "rapidapi-conversationllama"
# ==========================
# Load Environment Variables
# ==========================
load_dotenv()

gplaces_api_key = os.getenv("GPLACES_API_KEY")
if not gplaces_api_key:
    raise ValueError("Google Places API key (GPLACES_API_KEY) is not set in the environment.")

logger.debug(f"Loaded Google Maps API key: {'SET' if gplaces_api_key else 'NOT SET'}")

# ==========================
# Initialize LLM
# ==========================
llm = RapidAPIConversationLLaMA(rapidapi_key=os.getenv("RAPID_API_KEY"))

# ==========================
# Initialize Google Places Tool
# ==========================
try:
    # Preferred way: pass the API key directly
    location_tool = GooglePlacesTool(gplaces_api_key=gplaces_api_key)
except TypeError:
    # Fallback: manually create the API wrapper if the above fails
    api_wrapper = GooglePlacesAPIWrapper(gplaces_api_key=gplaces_api_key)
    location_tool = GooglePlacesTool(api_wrapper=api_wrapper)

# ==========================
# Initialize LangChain Agent
# ==========================
agent = initialize_agent(
    tools=[location_tool],
    llm=llm,
    verbose=True,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    handle_parsing_errors=True,
)

# ==========================
# Function to Find Nearby Places
# ==========================
def find_nearby_places(location: str):
    logger.info(f"Function called with location: {location}")

    def find_places(prompt: str) -> str:
        logger.info(f"find_places() received prompt: {prompt}")
        logger.debug("Running LangChain agent with location tool...")
        response = agent.run(prompt)
        logger.info("Agent run completed.")
        logger.debug(f"Agent response: {response}")
        return response

    return find_places(location)
