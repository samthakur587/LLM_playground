import streamlit as st
from unify import AsyncUnify
from unify import Unify
import os
import asyncio
import pandas as pd
# Define function to select model
def select_model():
    model_options = ["mixtral-8x7b-instruct-v0.1", "llama-2-13b-chat", "gemma-7b-it","codellama-34b-instruct","gpt-4-turbo","llama-3-8b-chat"]
    if 'vote_counts' not in st.session_state:
        st.session_state['vote_counts'] = {model: 0 for model in model_options}
    selected_model1 = st.sidebar.selectbox("Select your first model", model_options)
    selected_model2 = st.sidebar.selectbox("Select your seconed model 2", model_options)
    st.session_state['model1'] = selected_model1
    st.session_state['model2'] = selected_model2
    
# Define function to select provider
def select_provider():
    provider_options = ["anyscale", "together-ai", "fireworks-ai","openai","perplexity-ai"]
    selected_provider1 = st.sidebar.selectbox("Select provider for first model", provider_options)
    selected_provider2 = st.sidebar.selectbox("Select provider for seconed model", provider_options)
    st.session_state['provider1'] = selected_provider1
    st.session_state['provider2'] = selected_provider2
    
# Define function to input API key
def input_api_key():
    st.sidebar.subheader("Unify API Key")
    api_key = st.sidebar.text_input("Enter Unify API Key")
    if api_key is not st.session_state:
        st.session_state['api_key'] = api_key
        
def call_model(model='llama-2-13b-chat',provider='anyscale'):
    async_unify = AsyncUnify(
    api_key=st.session_state['api_key'],
    model=model,
    provider=provider)
    return async_unify

async def main():
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
    with provider_col:
        select_provider()
    col1, col2 = st.columns(2)
    # Display chat UI
    with col1:
        st.header("Model " + st.session_state['model1'])
        cont1 = st.container(height=500)
    with col2:
        st.header("Model " + st.session_state['model2'])
        cont2 = st.container(height=500)
    if prompt := st.chat_input("Say something"):
        cont1.write("🧑‍💻  " + prompt)
        cont2.write("🧑‍💻  "+ prompt)
        u1 = call_model(model=st.session_state['model1'], provider=st.session_state['provider1'])
        u2 = call_model(model=st.session_state['model2'], provider=st.session_state['provider2'])

        async def call(unify_obj, contain):
            try:
                async_stream = await unify_obj.generate(user_prompt=prompt, stream=True)
                placeholder = contain.empty()
                full_response = ''
                async for chunk in async_stream:
                    full_response += chunk
                    placeholder.markdown(full_response)
                placeholder.markdown("🤖  "+ full_response)
            except:
                contain.error(f"please change provider it's may be not provide this that you seleted ", icon="🚨")

        await asyncio.gather(
            call(u1, cont1),
            call(u2, cont2)
        )
    c1, c2= st.columns(2)
    # Display the vote buttons
    with c1:
        left_button_clicked = st.button("👍 Vote First Model")
        if left_button_clicked:
                # Increase the vote count for the selected model by 1 when the button is clicked
                model = st.session_state['model1']
                st.session_state['vote_counts'][model] += 1
    with c2:
        right_button_clicked = st.button("👍 Vote Second Model")
        if right_button_clicked:
                # Increase the vote count for the selected model by 1 when the button is clicked
                model2 = st.session_state['model2']
                st.session_state['vote_counts'][model2] += 1
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
    # Add custom CSS for the buttons

if __name__ == "__main__":
    asyncio.run(main())
    
    
     

