import streamlit as st
import pandas as pd
import helpers

st.set_page_config(
    page_title="Leaderboards",
    page_icon="📈",
    layout="wide",
)

source = "online" if st.session_state.source is True else "offline"

# Add custom CSS for the buttons
st.markdown(
    """
<h1 style='text-align: center; color: green;'>
    LeaderBoard For LLMs 🚀
</h1>
""",
    unsafe_allow_html=True,
)
# Create a DataFrame with the sorted vote counts
if source == "offline":
    vote_counts_df = pd.DataFrame(st.session_state.vote_counts)
    vote_counts_df["Model Name"] = vote_counts_df.index
    vote_counts_df[["Wins ⭐", "Losses ❌"]] = vote_counts_df[
        ["Wins ⭐", "Losses ❌"]
    ].add(st.session_state.offline_leaderboard[["Wins ⭐", "Losses ❌"]], fill_value=0)
    sorted_counts = vote_counts_df[["Model Name", "Wins ⭐", "Losses ❌"]]
    sorted_counts.sort_values(by=["Wins ⭐", "Losses ❌"], inplace=True)
    sorted_counts.index = range(sorted_counts.shape[0])

    detail_leaderboards = st.session_state.detailed_leaderboard["scores"].add(
        st.session_state.offline_detailed["scores"], fill_value=0
    )

    model_selection = list(detail_leaderboards.keys())
    detail_leaderboards = {"scores": detail_leaderboards}

if source == "online":
    helpers.database.get_online(True)
    detail_leaderboards = st.session_state.detailed_leaderboard["scores"].add(
        st.session_state.online_detailed["scores"], fill_value=0
    )

    model_selection = list(detail_leaderboards.keys())
    detail_leaderboards = {"scores": detail_leaderboards}

    vote_counts_df = pd.DataFrame(st.session_state.vote_counts)
    vote_counts_df[["Wins ⭐", "Losses ❌"]] = vote_counts_df[
        ["Wins ⭐", "Losses ❌"]
    ].add(st.session_state.online_leaderboard[["Wins ⭐", "Losses ❌"]], fill_value=0)
    vote_counts_df["Model Name"] = vote_counts_df.index
    sorted_counts = vote_counts_df[["Model Name", "Wins ⭐", "Losses ❌"]]
    sorted_counts.sort_values(by=["Wins ⭐", "Losses ❌"], inplace=True)
    sorted_counts.index = range(sorted_counts.shape[0])

sorted_counts_df = pd.DataFrame(
    sorted_counts, columns=["Model Name", "Wins ⭐", "Losses ❌"]
)
sorted_counts_df.style.hide()

with st.sidebar:
    enable_detail = st.checkbox(
        "Enable detailed view",
        value=st.session_state.enable_detail,
        on_change=lambda: setattr(
            st.session_state, "enable_detail", not st.session_state.enable_detail
        ),
    )

sorted_counts_detail = sorted_counts_df.assign(Compare=False)
sorted_counts_detail = sorted_counts_detail[
    ["Compare", "Model Name", "Wins ⭐", "Losses ❌"]
]

detail_leaderboards = st.session_state.detailed_leaderboard
model_selection = list(detail_leaderboards["scores"].keys())[1:]

if st.session_state.enable_detail:
    select_for_comparison = st.data_editor(
        sorted_counts_detail, num_rows="dynamic", use_container_width=True
    )
    models_to_compare = select_for_comparison.loc[select_for_comparison["Compare"]]

    model_names = models_to_compare["Model Name"]

    view_detail = detail_leaderboards["scores"].loc[model_names, model_names]

    with st.container(border=True):

        if not model_names.empty:
            st.markdown(
                "<h3 style='text-align: center; color: red;'>Detailed leaderboards:</h3>",
                unsafe_allow_html=True,
            )
            st.markdown(
                "<h5 style='text-align: center; color: white;'>The values represent the number of wins of the row model against the column model</h5>",
                unsafe_allow_html=True,
            )
            st.markdown(
                "<h5 style='text-align: center; color: white;'>(row, column) -> #row_wins</h5>",
                unsafe_allow_html=True,
            )
            st.write(view_detail)
        else:
            st.markdown(
                "<h3 style='text-align: center; color: red;'>Select the models to compare.</h3>",
                unsafe_allow_html=True,
            )
else:
    st.data_editor(sorted_counts_df, num_rows="dynamic", use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        model1_detail = st.selectbox("Select model 1", model_selection)
    with c2:
        model2_detail = st.selectbox("Select model 2", model_selection)
    with st.container(border=True):
        st.markdown(
            f"<h3 style='text-align: center; color: red;'>{model1_detail} : {model2_detail}</h3>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<h4 style='text-align: center;'>{int(detail_leaderboards['scores'].at[model1_detail, model2_detail])}:{int(detail_leaderboards['scores'].at[model2_detail, model1_detail])}</h4>",
            unsafe_allow_html=True,
        )
enable_global = st.sidebar.checkbox(
    "Enable global leaderboards",
    value=st.session_state.source,
    on_change=lambda: (
        setattr(st.session_state, "new_source", True),
        setattr(st.session_state, "source", not st.session_state.source),
    ),
)
source = "online" if enable_global is True else "offline"
if st.session_state.new_source in [True, None]:
    if source == "online":
        helpers.database.get_online(True)
    if source == "offline":
        helpers.database.get_offline(True)
    st.session_state.new_source = False
with st.sidebar:
    st.button("Save leaderboards", key="save")
    if st.session_state.save:

        helpers.database.save_offline()
        try:
            helpers.database.save_online()
        except Exception as e:
            st.write("Could not upload the results.")
            st.write(e)
