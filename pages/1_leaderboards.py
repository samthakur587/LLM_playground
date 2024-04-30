import streamlit as st
from unify import AsyncUnify
from unify import Unify
import os
from unify.exceptions import UnifyError
import asyncio
import pandas as pd
import json
import requests
import random

st.set_page_config(
    page_title="Leaderboards",
    page_icon="📈",
    layout="wide",
)

# Add custom CSS for the buttons
st.markdown(
"""
<h1 style='text-align: center; color: green;'>
    LeaderBoard For LLMs 🚀
</h1>
""",
unsafe_allow_html=True)
# Create a DataFrame with the sorted vote counts
sorted_counts = sorted(st.session_state['vote_counts'].items(), key=lambda x: x[1]["Wins ⭐"] + x[1]["Losses ❌"], reverse=True)
for idx, votes in enumerate(sorted_counts):
    sorted_counts[idx] = (votes[0], votes[1]["Wins ⭐"], votes[1]["Losses ❌"])
sorted_counts_df = pd.DataFrame(sorted_counts, columns=['Model Name', 'Wins ⭐', 'Losses ❌'])

st.data_editor(sorted_counts_df, num_rows="dynamic", use_container_width=True)


detail_leaderboards = st.session_state.detailed_leaderboards
model_selection = list(detail_leaderboards["scores"].keys())
c1, c2 = st.columns(2)
with c1:
    model1_detail = st.selectbox("Select model 1", model_selection, placeholder=model_selection[0])
with c2:
    model2_detail = st.selectbox("Select model 2", model_selection, placeholder=model_selection[1])
with st.container(border=True):
    st.markdown(f"<h3 style='text-align: center; color: red;'>{model1_detail} : {model2_detail}</h3>",
                unsafe_allow_html=True)
    st.markdown(f"<h4 style='text-align: center;'>{detail_leaderboards['scores'][model1_detail][model2_detail]}:{detail_leaderboards['scores'][model2_detail][model1_detail]}</h4>",
                unsafe_allow_html=True)

with open("detail_leaderboards.json", "w") as out_file:        
    json.dump(detail_leaderboards, out_file)
sorted_counts_df.to_csv('leaderboard.csv', index=False)