import streamlit as st
from streamlit_gsheets import GSheetsConnection
from unify import AsyncUnify
from unify import Unify
import os
from unify.exceptions import UnifyError
import asyncio
import pandas as pd
import json
import requests
import random



def get_database():

    keys = ["leaderboard", "detail", "models"]
    for key in keys:
        if key not in st.session_state.keys():
            st.session_state[key] = None

    if not os.path.exists("./models.json"):
        data = {"models": ["other"]}
        with open("models.json", "w") as out_file:
            json.dump(data, out_file)

    with open("models.json", "r") as f:
        data = json.load(f)

    all_models = tuple(data['models'])

    if not os.path.exists("./leaderboard.csv"):
        leaderboard = pd.DataFrame(["other", 0, 0], columns=["Model Name", "Wins ⭐", "Losses ❌"], index=["other"])
        leaderboard.to_csv("leaderboard.csv")

    data = pd.read_csv("leaderboard.csv")  # This will raise an error if the file does not exist
    json_data = {model: {"Wins ⭐": wins, "Losses ❌": losses} for model, wins, losses in zip(data["Model Name"], data["Wins ⭐"], data["Losses ❌"])}

    if 'vote_counts' not in st.session_state:
        st.session_state['vote_counts'] = json_data

    if not os.path.exists("./detail_leaderboards.json"):
        with open("detail_leaderboards.json", "w") as out_file:        
            detail_leaderboards = {"scores": {winning_model: {losing_model: 0 for losing_model in json_data.keys()} for winning_model in json_data.keys()}}
            json.dump(detail_leaderboards, out_file)

    if not os.path.exists("./detail_leaderboards.csv"):
        detail_dataframe = pd.DataFrame(data={winning_model: {losing_model: 0 for losing_model in json_data.keys()} for winning_model in json_data.keys()})
        detail_dataframe.index = list(json_data.keys())
        detail_dataframe.to_csv('detail_leaderboards.csv')

    with open("detail_leaderboards.csv", "r") as in_file:
        st.session_state.detail = pd.read_csv(in_file, index_col=0)

    st.session_state.leaderboard = json_data
    st.session_state.models = all_models
