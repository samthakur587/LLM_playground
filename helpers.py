import streamlit as st
from streamlit_gsheets import GSheetsConnection
import os
import pandas as pd
import json

leaderboard_worksheet_id = 0
detail_worksheet_id = 1113438455
models_worksheet_id = 1855482431


class database:

    def get_offline() -> None:
        """Static method. Assigns the local database's contents to the
        corresponding session states.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """

        keys = ["leaderboard", "detail", "models", "detailed_leaderboards"]
        for key in keys:
            if key not in st.session_state.keys():
                st.session_state[key] = None

        if not os.path.exists("./models.json"):
            data = {"models": ["other"]}
            with open("models.json", "w") as out_file:
                json.dump(data, out_file)

        with open("models.json", "r") as f:
            data = json.load(f)

        if not os.path.exists("./models.csv"):
            models_df = pd.DataFrame(data)
            models_df.to_csv("models.csv")

        all_models = tuple(data["models"])

        if not os.path.exists("./leaderboard.csv"):
            leaderboard = pd.DataFrame(
                ["other", 0, 0],
                columns=["Model Name", "Wins ⭐", "Losses ❌"],
                index=["other"],
            )
            leaderboard.to_csv("leaderboard.csv")

        data = pd.read_csv(
            "leaderboard.csv"
        )  # This will raise an error if the file does not exist
        json_data = {
            model: {"Wins ⭐": wins, "Losses ❌": losses}
            for model, wins, losses in zip(
                data["Model Name"], data["Wins ⭐"], data["Losses ❌"]
            )
        }

        if not os.path.exists("./detail_leaderboards.json"):
            with open("detail_leaderboards.json", "w") as out_file:
                detail_leaderboards = {
                    "scores": {
                        winning_model: {
                            losing_model: 0 for losing_model in json_data.keys()
                        }
                        for winning_model in json_data.keys()
                    }
                }
                json.dump(detail_leaderboards, out_file)

        if not os.path.exists("./detail_leaderboards.csv"):
            detail_dataframe = pd.DataFrame(
                data={
                    winning_model: {
                        losing_model: 0 for losing_model in json_data.keys()
                    }
                    for winning_model in json_data.keys()
                }
            )
            detail_dataframe.index = list(json_data.keys())
            detail_dataframe.to_csv("detail_leaderboards.csv")

        if not os.path.exists("./detail_leaderboards.json"):
            with open("detail_leaderboards.json", "w") as out_file:
                detail_leaderboards = {
                    "scores": {
                        winning_model: {
                            losing_model: 0 for losing_model in json_data.keys()
                        }
                        for winning_model in json_data.keys()
                    }
                }
                json.dump(detail_leaderboards, out_file)

        with open("detail_leaderboards.csv", "r") as in_file:
            st.session_state.detailed_leaderboards = {
                "scores": pd.read_csv(in_file, index_col=0)
            }

        st.session_state.leaderboard = json_data
        st.session_state.models = all_models

    def get_online():
        """Static method. Assigns the online database's contents to the
        corresponding session states.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """

        keys = [
            "leaderboard",
            "detail",
            "models",
            "online_leaderboard",
            "online_detailed",
            "online_models",
        ]
        for key in keys:
            if key not in st.session_state.keys():
                st.session_state[key] = None

        conn = st.connection("gsheets", type=GSheetsConnection)

        gsheets_leaderboard = conn.read(worksheet="leaderboard")
        gsheets_leaderboard.index = list(gsheets_leaderboard["Model Name"])
        gsheets_detail = conn.read(worksheet="detail_leaderboard")
        gsheets_models = conn.read(worksheet="models")
        gsheets_detail.index = list(gsheets_leaderboard["Model Name"])

        gsheets_leaderboard.dropna(axis=0, how="all", inplace=True)
        gsheets_leaderboard.dropna(axis=1, how="all", inplace=True)
        gsheets_detail.dropna(axis=0, how="all", inplace=True)
        gsheets_detail.dropna(axis=1, how="all", inplace=True)
        gsheets_models.dropna(axis=0, how="all", inplace=True)
        gsheets_models.dropna(axis=1, how="all", inplace=True)

        st.session_state.online_leaderboard = gsheets_leaderboard
        st.session_state.online_detailed = {"scores": gsheets_detail}
        st.session_state.online_models = gsheets_models["Models"]

        st.session_state.leaderboard = gsheets_leaderboard
        st.session_state.detailed_leaderboard = {"scores": gsheets_detail}
        st.session_state.models = gsheets_models["Models"]

        st.session_state.leaderboard.where(
            gsheets_leaderboard[["Wins ⭐", "Losses ❌"]] == 0, 0, inplace=True
        )
        st.session_state.detailed_leaderboard["scores"].where(gsheets_detail == 0, 0)

    def save_offline():
        """Static method. Saves the session states in the local database.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """

        keys = ["leaderboard", "detail", "models"]
        for key in keys:
            if key not in st.session_state.keys():
                st.session_state[key] = None

        sorted_counts = sorted(
            st.session_state["vote_counts"].items(),
            key=lambda x: x[1]["Wins ⭐"] + x[1]["Losses ❌"],
            reverse=True,
        )
        for idx, votes in enumerate(sorted_counts):
            sorted_counts[idx] = (votes[0], votes[1]["Wins ⭐"], votes[1]["Losses ❌"])
        sorted_counts_df = pd.DataFrame(
            sorted_counts, columns=["Model Name", "Wins ⭐", "Losses ❌"]
        )

        detail_leaderboards = st.session_state.detailed_leaderboards["scores"]

        detail_leaderboards.to_csv("detail_leaderboards.csv", index=False)
        sorted_counts_df.to_csv("leaderboard.csv", index=False)

    def save_online():
        """Static method. Saves the session states in the online database.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """

        keys = ["leaderboard", "detail", "models"]
        for key in keys:
            if key not in st.session_state.keys():
                st.session_state[key] = None

        sorted_counts = sorted(
            st.session_state["vote_counts"].items(),
            key=lambda x: x[1]["Wins ⭐"] + x[1]["Losses ❌"],
            reverse=True,
        )
        for idx, votes in enumerate(sorted_counts):
            sorted_counts[idx] = (votes[0], votes[1]["Wins ⭐"], votes[1]["Losses ❌"])

        sorted_counts_df = pd.DataFrame(
            sorted_counts, columns=["Model Name", "Wins ⭐", "Losses ❌"]
        )

        detail_leaderboards = st.session_state.detailed_leaderboards["scores"]

        models = st.session_state.models

        with st.echo():
            # Create GSheets connection
            conn_up = st.connection("gsheets", type=GSheetsConnection)

            # click button to update worksheet
            # This is behind a button to avoid exceeding Google API Quota

            conn_up.update(
                worksheet="leaderboard",
                data=sorted_counts_df,
            )

            conn_up.update(
                worksheet="detail_leaderboard",
                data=detail_leaderboards,
            )

            conn_up.update(
                worksheet="models",
                data=models,
            )
            st.cache_data.clear()
            st.experimental_rerun()

            # Display our Spreadsheet as st.dataframe
