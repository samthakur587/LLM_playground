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
sorted_counts = sorted(st.session_state['vote_counts'].items(), key=lambda x: x[1], reverse=True)
sorted_counts_df = pd.DataFrame(sorted_counts, columns=['Model Name', 'Wins ⭐', 'Losses ❌'])

st.data_editor(sorted_counts_df, num_rows="dynamic",use_container_width=True)

sorted_counts_df.to_csv('leaderboard.csv', index=False)