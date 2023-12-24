import streamlit as st
from openai import OpenAI
from conversation import run_conversation
from utils import get_data
from tools import *
import random
import pandas as pd


def main():
    # Configure the logging system
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    client = OpenAI()
    st.title("Gen-Insights")

    # Text input from the user
    st.sidebar.title("Common Questions")
    questions = {
        "My Own Stats": [
            "Which network I run in has the best CPI?",
            "My best performing country in terms of retention day 7. (Top 5 countries)"
        ],
        "General Benchmark Questions": [
            "Which benchmark networks have the best CPI?",
            "When looking at benchmark traffic, which country has the best retention day 7 rates? (Top 5 results)"
        ],
        "General Benchmark Questions (with specification)": [
            "best benchmark networks in terms of CPI in the united states",
            "which geos have good retention day 7 for googleadwords_int traffic?",
            "best CPI country for googleadwords_int?"
        ],
        "Direct Benchmark Comparison": [
            "My top 5 media sources' CPI compared to benchmark.",
            "How are my campaigns in each country compared to my direct competitors?"
        ],
        "Opportunities to Grow": [
            "For countries I don't currently run in, which ones have the best CPI? (Top 3)",
            "Which new media sources my competitors are running in, and I'm not? And what's their CPI? Order by their volume."
        ],
        "Trends": [
            "trendline over time for retention rate d7"
        ]
    }

    def create_question_buttons(category, questions):
        for question in questions:
            if st.sidebar.button(question):
                st.session_state.user_query = question

    for category, qs in questions.items():
        st.sidebar.subheader(category)
        create_question_buttons(category, qs)

    dfs_all = {}
    dfs_all['a_geo_all_apps'] = pd.read_parquet('obfus/a_geo_all_apps')
    dfs_all['a_ms_all_apps'] = pd.read_parquet('obfus/a_ms_all_apps')
    dfs_all['a_geo_ms_all_apps'] = pd.read_parquet('obfus/a_geo_ms_all_apps')
    dfs_all['b_geo_all_groups'] = pd.read_parquet('obfus/b_geo_all_groups')
    dfs_all['b_ms_all_groups'] = pd.read_parquet('obfus/b_ms_all_groups')
    dfs_all['b_geo_ms_all_groups'] = pd.read_parquet('obfus/b_geo_ms_all_groups')
    dfs_all['over_time_data'] = pd.read_parquet('obfus/over_time_data')
    dfs_all['over_time_slopes'] = pd.read_parquet('obfus/over_time_slopes')

    unique_app_ids = dfs_all['a_geo_all_apps']['app_id'].unique()  # Define unique_app_ids here
    # Negative trendline
    # 9cfbd2db48dd11f586550d1fcaeae22827e845dac7a74a98239f8f7c
    # faeeeabd0af4340095f58f97150c1251ed3a4a0bfbbd721e0a91401c
    # e795027c70bd7d3142b17bac695a5249dc15a9548d19976fa0aa8509
    # c95ba38d55b0e623d92b1283053d2970137923d1785330b7bc8714c5

    # Initialize session state for user_query, messages_so_far, and dfs_specific if they don't exist
    if 'user_query' not in st.session_state:
        st.session_state['user_query'] = ""
    if 'messages_so_far' not in st.session_state:
        st.session_state['messages_so_far'] = None
    if 'total_cost_so_far' not in st.session_state:
        st.session_state['total_cost_so_far'] = None
    if 'dfs_specific' not in st.session_state:
        first_app_id = unique_app_ids[0] if len(unique_app_ids) > 0 else None
        st.session_state['dfs_specific'] = get_data(dfs_all, first_app_id) if first_app_id else None
        st.session_state['selected_app_id'] = first_app_id  # Initialize selected_app_id with the first app_id
    def load_data_for_selected_app():
        app_id = st.session_state['selected_app_id']
        st.session_state['dfs_specific'] = get_data(dfs_all, app_id)
        st.session_state['messages_so_far'] = None  # Reset the context
        st.session_state['total_cost_so_far'] = 0

    _ = st.selectbox(
        'Pick an obfuscated app_id',
        unique_app_ids,
        index=0,  # Default to the first app_id in the list
        on_change=load_data_for_selected_app,
        key='selected_app_id'
    )

    if st.button("Generate random insight"):
        # Flatten the list of questions and pick a random one
        all_questions = [q for sublist in questions.values() for q in sublist]
        random_question = random.choice(all_questions)
        st.session_state.user_query = random_question

    _ = st.text_input("At your service. What would you like to know?", key="user_query")

    if st.button("Uncover"):
        user_input = st.session_state.user_query  # Retrieve the user query from the session state
        img = None  # Initialize img to None to ensure it's defined
        if user_input:
            logging.info(f'You entered: {user_input}')
            logging.info(f"App ID: {st.session_state['selected_app_id']}")
            funny_wait_sentences = [
                'Unearthing the data treasures...',
                'Crunching numbers harder than my morning cereal...',
                'Brewing a fresh pot of statistical insights...',
                'Putting the "dig" in "digits"... slotting pie charts into the oven...',
                'Sifting through bytes and bits for golden nuggets of wisdom...'
            ]

            with st.spinner(random.choice(funny_wait_sentences)):
                # Check if the data specific to the selected app is loaded
                if st.session_state['dfs_specific'] is not None:
                    # Run the conversation with the loaded data and existing messages
                    second_response_text, st.session_state['messages_so_far'], img, st.session_state['total_cost_so_far'] = run_conversation(
                        st.session_state['dfs_specific'], client, user_input,
                        st.session_state['messages_so_far'],
                        st.session_state['total_cost_so_far']
                    )
                    st.text(second_response_text)
                else:
                    # If the data is not loaded, display an error message
                    st.error("Data specific to the selected app is not loaded. Please select an app to load the data.")
        else:
            st.warning("Please enter a query to get insights.")

        # Check if img is not None and display it
        if img is not None:
            st.pyplot(img)

    if st.button("Reset context"):
        st.session_state['messages_so_far'] = None
        st.session_state['total_cost_so_far'] = None
        st.success("Context has been reset")


if __name__ == "__main__":
    main()
