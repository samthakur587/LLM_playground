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


    conn = st.connection("gsheets", type=GSheetsConnection)

    gsheets_leaderboard = conn.read(worksheet=0)
    gsheets_leaderboard.index = list(gsheets_leaderboard['Model Name'])
    gsheets_detail = conn.read(worksheet=1113438455)
    gsheets_detail.index = list(gsheets_detail.columns)[1:]
    gsheets_models = conn.read(worksheet=1855482431)

    st.session_state.leaderboard = gsheets_leaderboard
    st.session_state.detail = gsheets_detail
    st.session_state.models = gsheets_models
