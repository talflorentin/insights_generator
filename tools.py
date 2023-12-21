import logging
import json
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator

def my_own_stats(dfs, chosen_dimension, metric, num_results):
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


def general_benchmark_question(dfs, chosen_dimension, metric, num_results):
    df = dfs['b_ms'].copy() if chosen_dimension == "media_source" else dfs['b_geo'].copy()

    # First sort, by metric rank
    df['order_col'] = df['rnk_benchmark_group'].apply(lambda x: x.get(f'rank_best_{metric}', None)).copy()
    sorted_df = df.sort_values(by='order_col', ascending=False).head(num_results)

    # # Second sort, by volume
    # sorted_df['order_col'] = sorted_df['rnk_benchmark_group'].apply(lambda x: x.get(f'rank_total_installs', None)).copy()
    # sorted_df = sorted_df.sort_values(by='order_col', ascending=False).head(num_results)

    # TODO: improve the ordering system
    # Second sort, by metric itself
    sorted_df = sorted_df.sort_values(by=f'median_{metric}', ascending=True if metric == 'cpi' else False)

    output_json = {
        chosen_dimension: list(sorted_df[chosen_dimension]),
        f"{metric}": list(sorted_df[f'median_{metric}'])
    }
    logging.info(f'\noutput_json: {output_json}')
    return json.dumps(output_json, indent=2)


def opportunities_to_grow(dfs, chosen_dimension, metric, ordering_type, num_results):
    # Choose the appropriate dataframe and filter out rows that exist in a_geo or a_ms
    if chosen_dimension == "media_source":
        existing = set(dfs['a_ms'][chosen_dimension])
        df = dfs['b_ms'][~dfs['b_ms'][chosen_dimension].isin(existing)].copy()
    else:
        existing = set(dfs['a_geo'][chosen_dimension])
        df = dfs['b_geo'][~dfs['b_geo'][chosen_dimension].isin(existing)].copy()

    if ordering_type == 'total_installs':
        df['order_col'] = df['rnk_benchmark_group'].copy().apply(lambda x: x.get(f'rank_total_installs', None)).copy()
    else:
        df['order_col'] = df['rnk_benchmark_group'].copy().apply(lambda x: x.get(f'rank_best_{metric}', None)).copy()

    sorted_df = df.sort_values(by='order_col', ascending=False).head(num_results)
    sorted_df = sorted_df.sort_values(by=f'median_{metric}', ascending=False)
    output_json = {
        chosen_dimension: list(sorted_df[chosen_dimension]),
        f"{metric}": list(sorted_df[f'median_{metric}'])
    }
    logging.info(f'\noutput_json: {output_json}')
    return json.dumps(output_json, indent=2)


def compare_with_benchmark(dfs, chosen_dimension, metric, num_results):
    my_df = dfs['a_ms'].copy() if chosen_dimension == "media_source" else dfs['a_geo'].copy()
    benchmark_df = dfs['b_ms'].copy() if chosen_dimension == "media_source" else dfs['b_geo'].copy()
    comparison_df = my_df.merge(benchmark_df, on=chosen_dimension, suffixes=('_my', '_benchmark'))

    comparison_df['rank_total_installs'] = comparison_df['rnk_benchmark_group_my'].apply(
        lambda x: x.get('rank_total_installs', None))

    # TODO: right now sorts only by total installs
    comparison_df = comparison_df.sort_values(by='rank_total_installs', ascending=False)
    comparison_df = comparison_df.head(num_results)

    # Ratio compare
    percentage_diffs = []
    for my_value, benchmark_value in zip(comparison_df[metric], comparison_df[f'median_{metric}']):
        if benchmark_value != 0:  # To avoid division by zero
            percentage_diff = ((my_value - benchmark_value) / benchmark_value) * 100
        else:
            percentage_diff = 0  # You might want to handle this case differently
        percentage_diffs.append(round(percentage_diff, 3))  # Round to 3 decimal places
    comparison_df['percentage_diffs'] = percentage_diffs

    comparison_df = comparison_df.sort_values(by='percentage_diffs', ascending=False)
    output_json = {
        chosen_dimension: list(comparison_df[chosen_dimension]),
        f"my {metric}": list(comparison_df[metric]),
        f"benchmarks {metric}": list(comparison_df[f'median_{metric}']),
        f"percent difference from benchmark": list(comparison_df['percentage_diffs'])
    }
    logging.info(f'\noutput_json: {output_json}')
    return json.dumps(output_json, indent=2)


def general_benchmark_question_specific_segment(dfs, chosen_dimension_to_eval, metric, num_results, segment):
    # Use the b_geo_ms dataframe
    df = dfs['b_geo_ms'].copy()
    lock_column = 'country' if chosen_dimension_to_eval == "media_source" else 'media_source'
    df = df[df[lock_column] == segment]

    # First sort, by metric rank within the locked group
    order_column_name = f'rnk_benchmark_group_{lock_column}'
    df['order_col'] = df[order_column_name].apply(lambda x: x.get(f'rank_best_{metric}', None)).copy()
    sorted_df = df.sort_values(by='order_col', ascending=False).head(num_results)
    sorted_df = sorted_df.sort_values(by=f'median_{metric}', ascending=True if metric == 'cpi' else False)

    output_json = {
        chosen_dimension_to_eval: list(sorted_df[chosen_dimension_to_eval]),
        f"{metric}": list(sorted_df[f'median_{metric}'])
    }
    logging.info(f'\noutput_json: {output_json}')
    return json.dumps(output_json, indent=2)


def my_data_interpret(dfs):
    df1 = dfs['a_geo_ms'][['country', 'media_source', 'total_installs', 'cpi', 'ret_d7']].copy()
    df2 = dfs['a_ms'][['media_source', 'total_installs', 'cpi', 'ret_d7']].copy()
    df3 = dfs['a_geo'][['country', 'total_installs', 'cpi', 'ret_d7']].copy()

    output_json = {
        'country_and_media_source_combination_traffic': df1.to_csv(),
        'media_source_level_traffic': df2.to_csv(),
        'country_level_traffic': df3.to_csv(),
    }
    logging.info(f'\noutput_json: {output_json}')
    return json.dumps(output_json, indent=2)


def my_trends(dfs, limit):
    df_over_time = dfs['over_time_data'].copy()
    slopes_df = dfs['over_time_slopes'].copy()

    threshold = 0.1
    slopes_df = slopes_df[slopes_df.ret_d7_trend_diff_from_installs > threshold]

    app_slopes_df = slopes_df.sort_values(by='ret_d7_trend_diff_from_installs', ascending=False).head(limit)
    slopes_and_date_data = pd.merge(df_over_time, app_slopes_df, on=['app_id', 'media_source', 'country'])

    slopes_and_date_data = slopes_and_date_data.sort_values(by=['ret_d7_trend_diff_from_installs', 'install_date'],
                                                            ascending=[False, True])

    ## Output the data per day
    slopes_and_date_data = slopes_and_date_data[['media_source', 'country', 'install_date', 'ttl_installs', "ttl_users_d7"]]
    records_json = slopes_and_date_data.to_json(orient='records', date_format='iso')
    records = json.loads(records_json)
    output_dict = {col: [record[col] for record in records] for col in slopes_and_date_data.columns}
    print(output_dict)
    # output_json = json.dumps(output_dict, indent=2)
    # logging.info(f'\noutput_json: {output_json}')
    # return output_json

    ## Output the slopes summary
    app_slopes_df_subset = app_slopes_df[['media_source', 'country', 'slope_installs', 'slope_ret_d7']]
    numeric_cols = app_slopes_df_subset.select_dtypes(include=['number']).columns
    app_slopes_df_subset[numeric_cols] = app_slopes_df_subset[numeric_cols].round(decimals=3)
    output_json = {
        "country": list(app_slopes_df_subset.country),
        "media source": list(app_slopes_df_subset.media_source),
        "slope installs": list(app_slopes_df_subset.slope_installs),
        "slope retention day 7": list(app_slopes_df_subset.slope_ret_d7)
    }
    logging.info(f'\noutput_json: {output_json}')
    img = None
    if not slopes_and_date_data.empty:
        img = create_trendline_images(slopes_and_date_data)
    return json.dumps(output_json, indent=2), img


def create_trendline_images(slopes_and_date_data):
    # Convert 'install_date' to datetime if it's not already
    slopes_and_date_data['install_date'] = pd.to_datetime(slopes_and_date_data['install_date'])

    media_country_combinations = slopes_and_date_data[['media_source', 'country']].drop_duplicates()
    num_combinations = len(media_country_combinations)
    fig, axes = plt.subplots(nrows=num_combinations, ncols=1,
                             figsize=(10, 5 * num_combinations), squeeze=False)
    axes = axes.flatten()

    for (idx, (media_source, country)), ax in zip(media_country_combinations.iterrows(), axes):
        data = slopes_and_date_data[(slopes_and_date_data['media_source'] == media_source) &
                                    (slopes_and_date_data['country'] == country)]

        data = data.sort_values('install_date')
        ax.plot(data['install_date'], data['ttl_installs'], color='b', label='Total Installs')
        ax.set_ylabel('Total Installs', color='b')
        ax.tick_params(axis='y', labelcolor='b')

        # Set the x-ticks and labels
        ax.set_xticks(data['install_date'])
        ax.set_xticklabels(data['install_date'].dt.strftime('%Y-%m-%d'), rotation=90)

        ax2 = ax.twinx()
        ax2.plot(data['install_date'], data['ttl_users_d7'], color='r', label='Total Users D7')
        ax2.set_ylabel('Total Users D7', color='r')
        ax2.tick_params(axis='y', labelcolor='r')

        ax.set_title(f'Media Source: {media_source} | Country: {country}')
        ax.legend(loc='upper left')
        ax2.legend(loc='upper right')

    plt.tight_layout()  # Adjust subplots to fit into the figure area.
    return fig
