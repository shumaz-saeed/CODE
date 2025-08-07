import streamlit as st
import langchain_helper as lch


st.title("weather chatbot")
st.sidebar.header("select a city 🌆")
st.sidebar.selectbox("city", ['lahore', 'karachi', 'islamabad', 'peshawar', 'quetta'], key="city")

st.markdown(f'-----------------------------------------------\n  {lch.get_response("city")}\n-----------------------------------------------')