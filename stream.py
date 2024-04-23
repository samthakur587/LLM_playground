import streamlit as st
from unify import AsyncUnify
from unify import Unify
import os
import asyncio
import pandas as pd
import json
# Load JSON data from file
with open("models.json", "r") as f:
    data = json.load(f)
all_models = data['models']
model_options = [model.split("@")[0] for model in all_models]

def select_model():
    global model_options
    models = list(set(model_options))
    if 'vote_counts' not in st.session_state:
        st.session_state['vote_counts'] = {model: 0 for model in models}
    selected_model1 = st.sidebar.text_input("Enter Endpoint for First Model","mixtral-8x7b-instruct-v0.1@together-ai")
    selected_model2 = st.sidebar.text_input("Enter Endpoint for Seconed Model","llama-2-13b-chat@anyscale")
    st.session_state['model1'] = selected_model1
    st.session_state['model2'] = selected_model2

def history(model = 'model1',output='how are you'):
    if model == 'model1':
        st.session_state['chat_history1'].append({"role": "assistant", "content": output})
    elif model == 'model2':
        st.session_state['chat_history2'].append({"role": "assistant", "content": output})
    else:
        st.write("please enter the model1 or model2 in history function")
    if len(st.session_state['chat_history1'])>=10:
        st.session_state['chat_history1'].pop(0)
    if len(st.session_state['chat_history2'])>=10:
        st.session_state['chat_history2'].pop(0)

# Define function to input API key
def input_api_key():
    st.sidebar.subheader("Unify API Key")
    api_key = st.sidebar.text_input("UNIFY_KEY",type="password")
    if api_key is not st.session_state:
        st.session_state['api_key'] = api_key
def print_history(contai):
    cont1,cont2 = contai
    for i in st.session_state["chat_history1"]:
            if i['role']=="user":
                cont1.write("🧑‍💻" +"  "+ i["content"])
            else:
                cont1.write("🤖" +"  "+ i["content"])
    for i in st.session_state["chat_history2"]:
        if i['role']=="user": 
            cont2.write("🧑‍💻" +"  "+ i["content"])
        else:
            cont2.write("🤖" +"  "+ i["content"])       
def call_model(Endpoint):
    async_unify = AsyncUnify(
    api_key=st.session_state['api_key'],
    endpoint=Endpoint)
    return async_unify
st.set_option('deprecation.showPyplotGlobalUse', False)
async def main():
    code_input = ""
    st.set_page_config(layout="wide")
    st.markdown(
    """
    <h1 style='text-align: center; color: green;'>
        Unify's LLM Playground 🚀
    </h1>
    """,
    unsafe_allow_html=True)
    input_api_key()
    # Display sidebar widgets
    model_col, provider_col = st.sidebar.columns(2)
    with model_col:
        select_model()
    col11, col21 = st.columns(2)
    # Display chat UI
    with col11:
        st.markdown("<span style='font-size:20px; color:blue;'>Model " + st.session_state['model1'] + "</span>", unsafe_allow_html=True)
    with col21:
        st.markdown("<span style='font-size:20px; color:blue;'>Model " + st.session_state['model2'] + "</span>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        cont1 = st.container(height=500)
    with col2:
        cont2 = st.container(height=500)
    if "chat_history1" not in st.session_state:
        st.session_state["chat_history1"] = []
    if "chat_history2" not in st.session_state:
        st.session_state["chat_history2"] = []
    if prompt := st.chat_input("Say something"):
        st.session_state["chat_input"] = prompt
        code_input = prompt
        st.session_state['chat_history1'].append({"role": "user", "content": st.session_state["chat_input"]})
        st.session_state['chat_history2'].append({"role": "user", "content": st.session_state["chat_input"]})
        message1 = st.session_state['chat_history1']
        message2 = st.session_state['chat_history2']
        print_history(contai=(cont1,cont2))
        u1 = call_model(st.session_state['model1'])
        u2 = call_model(st.session_state['model2'])
        async def call(unify_obj,model,contain,message):
            try:
                async_stream = await unify_obj.generate(messages=message, stream=True)
                placeholder = contain.empty()
                full_response = ''
                async for chunk in async_stream:
                    full_response += chunk
                    placeholder.markdown(full_response)
                placeholder.markdown("🤖  "+ full_response)
                history(model = model,output=full_response)
            except:
                contain.error(f"please change provider it's may be not provide this that you seleted ", icon="🚨")

        await asyncio.gather(
            call(u1,model='model1', contain=cont1,message=message1),
            call(u2,model='model2', contain=cont2,message=message2)
        )
    c1, c2= st.columns(2)
    # Display the vote buttons
    with c1:
        left_button_clicked = st.button("👍 Vote First Model")
        if left_button_clicked:
                
                # Increase the vote count for the selected model by 1 when the button is clicked
                model = st.session_state['model1'].split("@")[0]
                st.session_state['vote_counts'][model] += 1
                print_history(contai=(cont1,cont2))
                code_input = st.session_state["chat_history2"][-2]['content']
    with c2:
        right_button_clicked = st.button("👍 Vote Second Model")
        if right_button_clicked:
                # Increase the vote count for the selected model by 1 when the button is clicked
                model2 = st.session_state['model2'].split("@")[0]
                st.session_state['vote_counts'][model2] += 1
                print_history(contai=(cont1,cont2))
                code_input = st.session_state["chat_history2"][-2]['content']
            # Add custom CSS for the buttons
    history_button_clicked = st.button("Clear Histroy")
    if history_button_clicked:
            st.session_state["chat_history1"] = []
            st.session_state["chat_history2"] = []
    # Add custom CSS for the buttons
    st.markdown(
    """
    <h1 style='text-align: center; color: green;'>
        LeaderBoard For LLMs 🚀
    </h1>
    """,
    unsafe_allow_html=True)
    # Create a DataFrame with the sorted vote counts
    sorted_counts = sorted(st.session_state['vote_counts'].items(), key=lambda x: x[1], reverse=True)
    sorted_counts_df = pd.DataFrame(sorted_counts, columns=['Model Name', 'Votes ⭐'])

    st.data_editor(sorted_counts_df, num_rows="dynamic",use_container_width=True)
    

    api1 = f'''
            # if you like first Model then you can add this in your code
            import os
            from unify import Unify
            unify = Unify(
                # This is the default and optional to include.
                api_key="your api key",
                endpoint="{st.session_state['model1']}"
            )
            response = unify.generate(user_prompt="{code_input}")
            '''
    api2 = f'''
            # if you like seconed Model then you can add this in your code
            import os
            from unify import Unify
            unify = Unify(
                # This is the default and optional to include.
                api_key="your api key",
                endpoint="{st.session_state['model2']}"
            )
            response = unify.generate(user_prompt="{code_input}")
            '''
    st.code(api1, language='python')
    st.code(api2, language='python')


if __name__ == "__main__":
    asyncio.run(main())
    
    
     

