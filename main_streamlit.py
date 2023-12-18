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

    # Initialize session state for user_query if it doesn't exist
    if 'user_query' not in st.session_state:
        st.session_state['user_query'] = ""
        st.session_state['messages_so_far'] = None

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

    def reset_messages():
        st.session_state['messages_so_far'] = None

    unique_app_ids = dfs_all['a_geo_all_apps']['app_id'].unique()
    selected_app_id = st.selectbox(
        'Pick an obfuscated app_id',
        unique_app_ids,
        on_change=reset_messages)
    st.session_state['selected_app_id'] = selected_app_id
    dfs_specific = get_data(dfs_all)

    if st.button("Generate random insight"):
        # Flatten the list of questions and pick a random one
        all_questions = [q for sublist in questions.values() for q in sublist]
        random_question = random.choice(all_questions)
        st.session_state.user_query = random_question

    user_input = st.text_input("At your service. What would you like to know?", key="user_query")

    if st.button("Uncover"):
        if user_input:
            logging.info(f'You entered: {user_input}')
            funny_wait_sentences = [
                'Unearthing the data treasures...',
                'Crunching numbers harder than my morning cereal...',
                'Brewing a fresh pot of statistical insights...',
                'Putting the "dig" in "digits"... slotting pie charts into the oven...',
                'Sifting through bytes and bits for golden nuggets of wisdom...'
            ]

            with st.spinner(random.choice(funny_wait_sentences)):
                second_response_text, st.session_state['messages_so_far'] = run_conversation(
                    dfs_specific, client, user_input, messages=st.session_state['messages_so_far']
                )
            st.text(second_response_text)
        else:
            st.warning("Please enter a query to get insights.")

    if st.button("Reset context"):
        st.session_state['messages_so_far'] = None
        st.success("Context has been reset")


if __name__ == "__main__":
    main()
