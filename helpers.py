import streamlit as st
from streamlit_gsheets import GSheetsConnection
import os
import pandas as pd
import json

leaderboard_worksheet_id = 0
detail_worksheet_id = 1113438455
models_worksheet_id = 1855482431


class database:

    @staticmethod
    def get_offline(update: bool = False) -> None:
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
        model_names = list(set([model.split("@")[0] for model in all_models]))
        if not os.path.exists("./leaderboard.csv"):
            leaderboard = pd.DataFrame({
                "Model Name": [model for model in model_names],
                "Wins ⭐": [0 for model in model_names],
                "Losses ❌": [0 for model in model_names],
            })
            leaderboard.to_csv("leaderboard.csv", index=False)

        data = pd.read_csv(
            "leaderboard.csv"
        )  # This will raise an error if the file does not exist
        json_data = {
            "Model Name": [model for model in data["Model Name"]],
            "Wins ⭐": [wins for wins in data["Wins ⭐"]],
            "Losses ❌": [losses for losses in data["Losses ❌"]],
        }

        if not os.path.exists("./detail_leaderboards.csv"):
            detail_dataframe = pd.DataFrame(
                data={
                    winning_model: {
                        losing_model: 0 for losing_model in json_data["Model Name"]
                    }
                    for winning_model in json_data["Model Name"]
                }
            )
            detail_dataframe.index = list(json_data["Model Name"])
            detail_dataframe.to_csv("detail_leaderboards.csv")

        with open("detail_leaderboards.csv", "r") as in_file:
            st.session_state.offline_detailed = pd.read_csv(in_file, index_col=0)

        st.session_state.offline_leaderboard = pd.DataFrame(json_data)
        st.session_state.offline_leaderboard.set_index(
            "Model Name", inplace=True, drop=False
        )
        st.session_state.offline_models = all_models

        if not update:
            st.session_state.leaderboard = pd.DataFrame(json_data)
            st.session_state.models = st.session_state.offline_models

            st.session_state.leaderboard[["Wins ⭐", "Losses ❌"]] = (
                st.session_state.leaderboard[["Wins ⭐", "Losses ❌"]].where(
                    st.session_state.leaderboard[["Wins ⭐", "Losses ❌"]] == 0, 0
                )
            )

    @staticmethod
    def get_online(update: bool = False):
        """Static method. Assigns the online database's contents to the
        corresponding session states.

        Parameters
        ----------
            update
                if True, the session states with the new votes will not get reset, only the full leaderboards
                will be refreshed. Used to ensure that the online database will get correctly updated.
                Default: False

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

        if "Unnamed: 0" in list(gsheets_detail.columns):
            gsheets_detail.drop("Unnamed: 0", axis=1, inplace=True)

        st.session_state.online_leaderboard = gsheets_leaderboard.convert_dtypes()
        st.session_state.online_detailed = gsheets_detail.convert_dtypes()
        st.session_state.online_models = gsheets_models["Models"]

        st.session_state.online_leaderboard.set_index(
            "Model Name", inplace=True, drop=False
        )

        if not update:
            st.session_state.leaderboard = gsheets_leaderboard
            st.session_state.models = gsheets_models["Models"]

            st.session_state.leaderboard[["Wins ⭐", "Losses ❌"]] = (
                st.session_state.leaderboard[["Wins ⭐", "Losses ❌"]].where(
                    gsheets_leaderboard[["Wins ⭐", "Losses ❌"]] == 0, 0
                )
            )

            st.session_state.leaderboard = st.session_state.leaderboard.convert_dtypes()

    @staticmethod
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
        database.get_offline(True)
        vote_counts_df = st.session_state.vote_counts
        vote_counts_df_added = vote_counts_df[["Wins ⭐", "Losses ❌"]].add(
            st.session_state.offline_leaderboard[["Wins ⭐", "Losses ❌"]], fill_value=0
        )
        sorted_counts_df = vote_counts_df_added[["Wins ⭐", "Losses ❌"]]
        sorted_counts_df["Model Name"] = sorted_counts_df.index
        sorted_counts_df = sorted_counts_df[["Model Name", "Wins ⭐", "Losses ❌"]]

        sorted_counts_df.sort_values(by=["Wins ⭐", "Losses ❌"], inplace=True)

        detail_leaderboards = st.session_state.detailed_leaderboards.add(
            st.session_state.offline_detailed, fill_value=0
        )
        detail_leaderboards.index = detail_leaderboards.columns

        models = pd.DataFrame({"Models": st.session_state.models})

        detail_leaderboards.to_csv("detail_leaderboards.csv", index=True)
        sorted_counts_df.to_csv("leaderboard.csv", index=False)
        models.to_csv("models.csv", index=False)

    @staticmethod
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
        database.get_online(True)

        vote_counts_df = pd.DataFrame(st.session_state.vote_counts)
        vote_counts_df_added = vote_counts_df[["Wins ⭐", "Losses ❌"]].add(
            st.session_state.online_leaderboard[["Wins ⭐", "Losses ❌"]], fill_value=0
        )
        sorted_counts_df = vote_counts_df_added[["Wins ⭐", "Losses ❌"]]
        sorted_counts_df["Model Name"] = sorted_counts_df.index
        sorted_counts_df = sorted_counts_df[["Model Name", "Wins ⭐", "Losses ❌"]]

        sorted_counts_df.sort_values(by=["Wins ⭐", "Losses ❌"], inplace=True)

        detail_leaderboards = st.session_state.detailed_leaderboards.add(
            st.session_state.offline_detailed, fill_value=0
        )
        detail_leaderboards.index = detail_leaderboards.columns
        try:
            detail_leaderboards.insert(0, "", detail_leaderboards.index)
        except ValueError:
            pass

        models = pd.DataFrame({"Models": st.session_state.models})

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
            st.rerun()


def init_session(mode: str = "keys") -> None:
    """Initialize session states and databases.

    Parameters
    ----------
    mode
        defines elements to assign.
        - ''keys'': initializes keys for st.session_state elements.
        - ''online'': connects to the database (Google Sheets) and assigns its contents to
            their corresponding session states.
        - ''offline': loads the database from the project's folder and assigns its contents
            to their corresponding session states.
        Default: "keys".

    Returns
    -------
    None
    """

    global all_models, data, json_data
    if mode == "keys":
        keys = [
            "chat_input",
            "api_key_provided",
            "vote1",
            "vote2",
            "model1",
            "model2",
            "scores",
            "authenticated",
            "new_models_selected",
            "detail",
            "new_source",
            "saved",
        ]
        for key in keys:
            if key not in st.session_state.keys():
                st.session_state[key] = None
        if "code_input" not in st.session_state.keys():
            st.session_state.code_input = " "
        if "chat_history1" not in st.session_state.keys():
            st.session_state.chat_history1 = []
        if "chat_history2" not in st.session_state.keys():
            st.session_state.chat_history2 = []

        if "model1_selectbox" not in st.session_state.keys():
            st.session_state.placeholder_model1 = "other"
            st.session_state.model1_selectbox = None
        if "model1_other" not in st.session_state.keys():
            st.session_state.placeholder_model1_other = "model@provider"
        if "model2_selectbox" not in st.session_state.keys():
            st.session_state.placeholder_model2 = "other"
            st.session_state.model2_selectbox = None
        if "model2_other" not in st.session_state.keys():
            st.session_state.placeholder_model2_other = "model@provider"

        if "index_model1" not in st.session_state.keys():
            st.session_state.index_model1 = 0
        if "index_model2" not in st.session_state.keys():
            st.session_state.index_model2 = 0

        if "value_model1_other" not in st.session_state.keys():
            st.session_state.value_model1_other = ""
        if "value_model2_other" not in st.session_state.keys():
            st.session_state.value_model2_other = ""

        if "api_key" not in st.session_state.keys():
            st.session_state.api_key = ""

        if "source" not in st.session_state.keys():
            st.session_state.source = False

        if "vote_counts" not in st.session_state:
            st.session_state.vote_counts = pd.DataFrame(
                {"Model Name": ["other"], "Wins ⭐": [0], "Losses ❌": [0]}
            )
            st.session_state.vote_counts.set_index(
                "Model Name", inplace=True, drop=False
            )

        if "detailed_leaderboards" not in st.session_state:
            st.session_state.detailed_leaderboards = pd.DataFrame({"other": [0]})
            st.session_state.detailed_leaderboards.insert(
                0, "", st.session_state.detailed_leaderboards.columns
            )
            st.session_state.detailed_leaderboards.set_index(
                "", inplace=True, drop=True
            )

        if "enable_detail" not in st.session_state.keys():
            st.session_state.enable_detail = False

        if "winner_selected" not in st.session_state.keys():
            st.session_state.winner_selected = True
        if "prompt_provided" not in st.session_state.keys():
            st.session_state.prompt_provided = False

        if (
            "themes" not in st.session_state
        ):  # Source of the themes solution: https://discuss.streamlit.io/t/changing-the-streamlit-theme-with-a-toggle-button-solution/56842/2
            st.session_state.themes = {
                "current_theme": "light",
                "refreshed": True,
                "light": {
                    "theme.base": "dark",
                    # "theme.backgroundColor": "black",
                    # "theme.primaryColor": "#c98bdb",
                    # "theme.secondaryBackgroundColor": "#5591f5",
                    # "theme.textColor": "white",
                    "button_face": "🌜",
                },
                "dark": {
                    "theme.base": "light",
                    # "theme.backgroundColor": "white",
                    # "theme.primaryColor": "#5591f5",
                    # "theme.secondaryBackgroundColor": "#82E1D7",
                    # "theme.textColor": "#0a1464",
                    "button_face": "🌞",
                },
            }

    if mode == "offline":
        database.get_offline(st.session_state.new_source is True)
        # Load JSON data from file
        all_models = st.session_state.models
        # model_options = [model.split("@")[0] for model in all_models]
        data = pd.read_csv(
            "leaderboard.csv"
        )  # This will raise an error if the file does not exist
        st.session_state.leaderboard.set_index("Model Name", inplace=True, drop=False)
        json_data = st.session_state.leaderboard

        # st.session_state["vote_counts"] = pd.DataFrame(
        #     json_data, columns=["Model Name", "Wins ⭐", "Losses ❌"]
        # )

    if mode == "online":
        database.get_online(st.session_state.new_source is True)
        all_models = list(st.session_state.models)
        json_data = st.session_state.leaderboard
        data = {model: 0 for model in json_data.index}
        # st.session_state["vote_counts"] = json_data


def ChangeTheme():
    previous_theme = st.session_state.themes["current_theme"]
    tdict = (
        st.session_state.themes["light"]
        if st.session_state.themes["current_theme"] == "light"
        else st.session_state.themes["dark"]
    )
    for vkey, vval in tdict.items():
        if vkey.startswith("theme"):
            st._config.set_option(vkey, vval)

    st.session_state.themes["refreshed"] = False
    if previous_theme == "dark":
        st.session_state.themes["current_theme"] = "light"
    elif previous_theme == "light":
        st.session_state.themes["current_theme"] = "dark"


class Buttons:

    @staticmethod
    def change_theme_button() -> None:
        """The button to switch between the light and dark modes.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        btn_face = (
            st.session_state.themes["light"]["button_face"]
            if st.session_state.themes["current_theme"] == "light"
            else st.session_state.themes["dark"]["button_face"]
        )
        st.button(btn_face, on_click=ChangeTheme)

        if st.session_state.themes["refreshed"] is False:
            st.session_state.themes["refreshed"] = True
            st.rerun()

    @staticmethod
    def left_button_clicked(
        cont1: st.container = None, cont2: st.container = None
    ) -> None:
        """The button to select the model on the left side as the winning
        model.

        Parameters
        ----------
        cont1
            The chat window containing the chat history with the left-side model.
        cont2
            The chat window containing the chat history with the right-side model.

        Returns
        -------
        None
        """
        assert cont1 is not None
        assert cont2 is not None
        st.balloons()
        # Increase the vote count for the selected model by 1 when the button is clicked
        model1 = st.session_state["model1"].split("@")[0]
        model2 = st.session_state["model2"].split("@")[0]

        st.session_state["vote_counts"].at[model1, "Wins ⭐"] += 1
        st.session_state["vote_counts"].at[
            st.session_state["model2"].split("@")[0], "Losses ❌"
        ] += 1
        if (
            model1 not in st.session_state.detailed_leaderboards.keys()
            or model1 not in st.session_state.detailed_leaderboards.keys()
        ):
            st.session_state.detailed_leaderboards.at[model1, model2] = 0
        st.session_state.detailed_leaderboards.at[model1, model2] += 1

        print_history(contain=(cont1, cont2))
        try:
            st.session_state.code_input = st.session_state["chat_history1"][-2][
                "content"
            ]
        except IndexError:
            st.session_state.code_input = " "

    @staticmethod
    def right_button_clicked(
        cont1: st.container = None, cont2: st.container = None
    ) -> None:
        """The button to select the model on the right side as the winning
        model.

        Parameters
        ----------
        cont1
            The chat window containing the chat history with the left-side model.
        cont2
            The chat window containing the chat history with the right-side model.

        Returns
        -------
        None
        """
        assert cont1 is not None
        assert cont2 is not None
        st.balloons()
        # Increase the vote count for the selected model by 1 when the button is clicked
        model1 = st.session_state["model1"].split("@")[0]
        model2 = st.session_state["model2"].split("@")[0]

        st.session_state["vote_counts"].at[model2, "Wins ⭐"] += 1
        st.session_state["vote_counts"].at[
            st.session_state["model1"].split("@")[0], "Losses ❌"
        ] += 1
        if (
            model2 not in st.session_state.detailed_leaderboards.index
            or model1 not in st.session_state.detailed_leaderboards.index
        ):
            st.session_state.detailed_leaderboards.at[model2, model1] = 0
        st.session_state.detailed_leaderboards.at[model2, model1] += 1

        print_history(contain=(cont1, cont2))
        try:
            st.session_state.code_input = st.session_state["chat_history2"][-2][
                "content"
            ]
        except IndexError:
            st.session_state.code_input = " "

    @staticmethod
    def tie_button(cont1: st.container = None, cont2: st.container = None) -> None:
        """The button to declare a tie.

        Parameters
        ----------
        cont1
            The chat window containing the chat history with the left-side model.
        cont2
            The chat window containing the chat history with the right-side model.

        Returns
        -------
        None
        """
        assert cont1 is not None
        assert cont2 is not None
        st.balloons()
        # Increase the vote count for the selected model by 1 when the button is clicked
        model1 = st.session_state["model1"].split("@")[0]
        model2 = st.session_state["model2"].split("@")[0]

        st.session_state["vote_counts"].at[model2, "Wins ⭐"] += 1
        st.session_state["vote_counts"].at[model1, "Wins ⭐"] += 1
        if (
            model2 not in st.session_state.detailed_leaderboards.index
            or model1 not in st.session_state.detailed_leaderboards.index
        ):
            st.session_state.detailed_leaderboards.at[model2, model1] = 0
            st.session_state.detailed_leaderboards.at[model1, model2] = 0
        st.session_state.detailed_leaderboards.at[model2, model1] += 1
        st.session_state.detailed_leaderboards.at[model1, model2] += 1

        print_history(contain=(cont1, cont2))
        try:
            st.session_state.code_input = st.session_state["chat_history2"][-2][
                "content"
            ]
        except IndexError:
            st.session_state.code_input = " "

    @staticmethod
    def no_win_button(cont1: st.container = None, cont2: st.container = None) -> None:
        """The button to declare that both models provided bad answers.

        Parameters
        ----------
        cont1
            The chat window containing the chat history with the left-side model.
        cont2
            The chat window containing the chat history with the right-side model.

        Returns
        -------
        None
        """
        assert cont1 is not None
        assert cont2 is not None
        st.balloons()
        # Increase the vote count for the selected model by 1 when the button is clicked
        model1 = st.session_state["model1"].split("@")[0]
        model2 = st.session_state["model2"].split("@")[0]

        st.session_state["vote_counts"].at[model2, "Losses ❌"] += 1
        st.session_state["vote_counts"].at[model1, "Losses ❌"] += 1
        if (
            model2 not in st.session_state.detailed_leaderboards.index
            or model1 not in st.session_state.detailed_leaderboards.index
        ):
            st.session_state.detailed_leaderboards.at[model2, model1] = 0
            st.session_state.detailed_leaderboards.at[model1, model2] = 0

        print_history(contain=(cont1, cont2))
        try:
            st.session_state.code_input = st.session_state["chat_history2"][-2][
                "content"
            ]
        except IndexError:
            st.session_state.code_input = " "

    @staticmethod
    def save_button() -> None:
        """Update the leaderboards with the results from the session.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        st.button(
            "Save leaderboards",
            on_click=lambda: setattr(st.session_state, "saved", True),
        )

        if st.session_state.saved:
            st.write(st.session_state.detailed_leaderboards)
            st.session_state.saved = False
            database.save_offline()
            try:
                database.save_online()
            except Exception as e:
                st.write("Could not upload the results.")
                st.write(e)
            finally:
                for key in st.session_state.keys():
                    del st.session_state[key]


def print_history(contain: tuple[st.container]) -> None:
    """Print the chat history in a streamlit split container.

    Parameters
    ----------
    contain
        streamlit container to print the chat history into.

    Returns
    -------
    None
    """

    cont1, cont2 = contain
    for i in st.session_state["chat_history1"]:
        if i["role"] == "user":
            cont1.write("🧑‍💻" + "  " + i["content"])
        else:
            cont1.write(i["content"])
    for i in st.session_state["chat_history2"]:
        if i["role"] == "user":
            cont2.write("🧑‍💻" + "  " + i["content"])
        else:
            cont2.write(i["content"])
