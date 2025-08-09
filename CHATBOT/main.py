
import streamlit as st
from langchain_helper import get_response 

st.title("LangChain Agent with Streamlit")
st.write("This is a simple interface to interact with your LangChain agent.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = get_response(prompt)
            st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
