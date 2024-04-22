import streamlit as st
from unify import AsyncUnify
from unify import Unify
import os
import asyncio
# Define function to display chat UI
def chat_ui():
    st.title("Chat UI")
    # Chat UI code goes here
    st.text_area("Chat", height=500, max_chars=1000, key="chat_input")
    st.button("Send", key="send_button")

# Define function to select model
def select_model():
    model_options = ["mixtral-8x7b-instruct-v0.1", "llama-2-13b-chat", "gemma-7b-it"]
    selected_model1 = st.sidebar.selectbox("Select model 1", model_options)
    selected_model2 = st.sidebar.selectbox("Select model 2", model_options)
    st.session_state['model1'] = selected_model1
    st.session_state['model2'] = selected_model2
    

# Define function to select provider
def select_provider():
    provider_options = ["anyscale", "together-ai", "fireworks-ai"]
    selected_provider1 = st.sidebar.selectbox("Select provider 1", provider_options)
    selected_provider2 = st.sidebar.selectbox("Select provider 2", provider_options)
    st.session_state['provider1'] = selected_provider1
    st.session_state['provider2'] = selected_provider2
    

# Define function to input API key
def input_api_key():
    st.sidebar.subheader("API Key")
    api_key = st.sidebar.text_input("Enter Unify API Key")
    if api_key is not st.session_state:
        st.session_state['api_key'] = api_key

# def chat_actions(output1,output2):
#     st.session_state["chat_history"].append(
#         {"role": "user", "content": st.session_state["chat_input"]},
#     )

#     st.session_state["chat_history"].append(
#         {
#             "role": "assistant",
#             "content": "how are you",
#         },  # This can be replaced with your chat response logic
#     )

def history(model = 'model1',output='how are you'):
    if model == 'model1':
        st.session_state['chat_history1'].append({"role": "user", "content": st.session_state["chat_input"]})
        st.session_state['chat_history1'].append({"role": "assistant", "content": output})
    elif model == 'model2':
        st.session_state['chat_history2'].append({"role": "user", "content": st.session_state["chat_input"]})
        st.session_state['chat_history2'].append({"role": "assistant", "content": output})
    else:
        st.write("please enter the model1 or model2 in history function")
    if len(st.session_state['chat_history1'])>=10:
        st.session_state['chat_history1'].pop(0)
    if len(st.session_state['chat_history2'])>=10:
        st.session_state['chat_history2'].pop(0)
def call_model(model='llama-2-13b-chat',provider='anyscale',input='hii'):
    unify = Unify(
    # This is the default and optional to include.
    api_key=st.session_state['api_key'] ,
    model=model,
    provider=provider)
    response = unify.generate(user_prompt=input)
    return response
# Main function to run the app
def main():
    st.set_page_config(layout="wide")
    input_api_key()
    # Display sidebar widgets
    model_col, provider_col = st.sidebar.columns(2)
    with model_col:
        select_model()
    with provider_col:
        select_provider()
    col1, col2 = st.columns(2)
    if "chat_history1" not in st.session_state:
        st.session_state["chat_history1"] = []
    if "chat_history2" not in st.session_state:
        st.session_state["chat_history2"] = []
    # Display chat UI
    with col1:
        st.header("Model " + st.session_state['model1'])
        cont1 = st.container(height=500)
    with col2:
        st.header("Model " + st.session_state['model2'])
        cont2 = st.container(height=500)
    if st.button('clear history'):
        st.session_state["chat_history1"] = []
        st.session_state["chat_history2"] = []
    if prompt := st.chat_input("Say something"):
        st.session_state["chat_input"] = prompt
        output1 = call_model(model=st.session_state['model1'] ,provider=st.session_state['provider1'],input=prompt)
        output2 = call_model(model=st.session_state['model1'] ,provider=st.session_state['provider1'],input=prompt)
        history(model='model1',output=output1)
        history(model='model2',output=output2)
        for i in st.session_state["chat_history1"]:
            #cont1.write("🧑‍💻" +"  "+ i["content"])
            cont1.write("🤖" +"  "+ i["content"])
        for i in st.session_state["chat_history2"]: 
            #cont2.write("🧑‍💻" +"  "+ i["content"])
            cont2.write("🤖" +"  "+ i["content"])
        


if __name__ == "__main__":
    main()
