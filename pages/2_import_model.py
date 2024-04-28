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
    page_title="Import model",
    page_icon="📝",
    layout="wide",
)
code_input = st.session_state.code_input
api1 = f'''
        # if you like the {st.session_state.model1} model, then you can add this to your code:
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
        # if you like the {st.session_state.model2} model, then you can add this to your code:
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