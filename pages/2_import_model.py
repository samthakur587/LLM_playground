import streamlit as st
import helpers

st.set_page_config(
    page_title="Import Model",
    page_icon="📝",
    layout="wide",
)

_, theme_col = st.column([7, 1])
with theme_col:
    helpers.change_theme_button()

code_input = st.session_state.code_input
api1 = f"""
        # if you like the {st.session_state.model1} model, then you can add this to your code:
        import os
        from unify import Unify
        unify = Unify(
            # This is the default and optional to include.
            api_key="your api key",
            endpoint="{st.session_state['model1']}"
        )
        response = unify.generate(user_prompt="{code_input}")
        """
api2 = f"""
        # if you like the {st.session_state.model2} model, then you can add this to your code:
        import os
        from unify import Unify
        unify = Unify(
            # This is the default and optional to include.
            api_key="your api key",
            endpoint="{st.session_state['model2']}"
        )
        response = unify.generate(user_prompt="{code_input}")
        """
st.code(api1, language="python")
st.code(api2, language="python")
