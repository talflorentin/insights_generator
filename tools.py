import logging
import json

def my_own_stats(dfs, chosen_dimension, metric, ordering_type, num_results):
    df = dfs['a_ms'].copy() if chosen_dimension == "media_source" else dfs['a_geo'].copy()
    df['order_col'] = df['rnk_benchmark_group'].apply(lambda x: x.get(f'rank_best_{metric}', None)).copy()
    sorted_df = df.sort_values(by='order_col', ascending=False).head(num_results)
    sorted_df = sorted_df.sort_values(by=metric, ascending=False)
    output_json = {
        chosen_dimension: list(sorted_df[chosen_dimension]),
        f"{metric}": list(sorted_df[metric])
    }
    logging.info(f'\noutput_json: {output_json}')
    return json.dumps(output_json, indent=2)


def general_benchmark_question(dfs, chosen_dimension, metric, ordering_type, num_results):
    df = dfs['b_ms'].copy() if chosen_dimension == "media_source" else dfs['b_geo'].copy()

    df['order_col'] = df['rnk_benchmark_group'].apply(lambda x: x.get(f'rank_best_{metric}', None)).copy()
    sorted_df = df.sort_values(by='order_col', ascending=False).head(num_results)
    sorted_df = sorted_df.sort_values(by=f'median_{metric}', ascending=True if metric == 'cpi' else False)
    output_json = {
        chosen_dimension: list(sorted_df[chosen_dimension]),
        f"{metric}": list(sorted_df[f'median_{metric}'])
    }
    logging.info(f'\noutput_json: {output_json}')
    return json.dumps(output_json, indent=2)
