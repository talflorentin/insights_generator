from openai import OpenAI
import logging
from conversation import run_conversation
from utils import get_data
import pandas as pd


def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s')

    client = OpenAI()
    messages_so_far = None

    dfs_all = {}
    dfs_all['a_geo_all_apps'] = pd.read_parquet('obfus/a_geo_all_apps')
    dfs_all['a_ms_all_apps'] = pd.read_parquet('obfus/a_ms_all_apps')
    dfs_all['a_geo_ms_all_apps'] = pd.read_parquet('obfus/a_geo_ms_all_apps')
    dfs_all['b_geo_all_groups'] = pd.read_parquet('obfus/b_geo_all_groups')
    dfs_all['b_ms_all_groups'] = pd.read_parquet('obfus/b_ms_all_groups')
    dfs_all['b_geo_ms_all_groups'] = pd.read_parquet('obfus/b_geo_ms_all_groups')

    dfs_specific = get_data(dfs_all)
    while True:
        if messages_so_far is None:
            user_input = input("Gen-Insights at your service. What would you like to know?\n")
        else:
            user_input = input()
        if user_input == 'q':
            break
        logging.info(f'You entered: {user_input}')
        second_response_text, messages_so_far = run_conversation(dfs_specific, client, user_input, messages=messages_so_far)
        print(second_response_text)


if __name__ == "__main__":
    main()
