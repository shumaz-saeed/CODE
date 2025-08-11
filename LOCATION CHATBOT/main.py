import streamlit as st
from langchain_helper import find_nearby_places



st.title("THE FINDER")

st.text_input("Enter your prompt", key= "prompt")

result = find_nearby_places(st.session_state.prompt)

st.text(result) 
