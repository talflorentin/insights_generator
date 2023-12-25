import pandas as pd
from constants import *
from tools import *


def get_data(full_dfs, chosen_app_id=None):
    a_geo_all_apps = full_dfs['a_geo_all_apps']
    a_ms_all_apps = full_dfs['a_ms_all_apps']
    a_geo_ms_all_apps = full_dfs['a_geo_ms_all_apps']
    b_geo_all_groups = full_dfs['b_geo_all_groups']
    b_ms_all_groups = full_dfs['b_ms_all_groups']
    b_geo_ms_all_groups = full_dfs['b_geo_ms_all_groups']
    over_time_data = full_dfs['over_time_data']
    over_time_slopes = full_dfs['over_time_slopes']

    if chosen_app_id is None:
        high_ms_count_group = b_ms_all_groups.benchmark_group.value_counts().index[0]
        chosen_app_id = a_ms_all_apps[a_ms_all_apps.benchmark_group == high_ms_count_group].app_id.value_counts().index[0]

    a_geo = a_geo_all_apps[a_geo_all_apps.app_id.isin([chosen_app_id])]
    a_ms = a_ms_all_apps[a_ms_all_apps.app_id.isin([chosen_app_id])]
    a_geo_ms = a_geo_ms_all_apps[a_geo_ms_all_apps.app_id.isin([chosen_app_id])]
    over_time_data = over_time_data[over_time_data.app_id.isin([chosen_app_id])]
    over_time_slopes = over_time_slopes[over_time_slopes.app_id.isin([chosen_app_id])]

    chosen_benchmark_group = a_geo.benchmark_group.unique()[0]
    b_geo = b_geo_all_groups[b_geo_all_groups.benchmark_group.isin([chosen_benchmark_group])]
    b_ms = b_ms_all_groups[b_ms_all_groups.benchmark_group.isin([chosen_benchmark_group])]
    b_geo_ms = b_geo_ms_all_groups[b_geo_ms_all_groups.benchmark_group.isin([chosen_benchmark_group])]
    return {"b_geo_ms": b_geo_ms, "b_ms": b_ms, "b_geo": b_geo,
            "a_geo_ms": a_geo_ms, "a_ms": a_ms, "a_geo": a_geo,
            "b_geo_ms_all_groups": b_geo_ms_all_groups, "b_ms_all_groups": b_ms_all_groups,
            "b_geo_all_groups": b_geo_all_groups, "a_geo_ms_all_apps": a_geo_ms_all_apps,
            "a_ms_all_apps": a_ms_all_apps, "a_geo_all_apps": a_geo_all_apps,
            "over_time_data": over_time_data, "over_time_slopes": over_time_slopes}


def get_answer_to_ua_question(dfs, function, metric, group, ordering_type, limit, segment):
    metric = 'cpi' if metric == 'CPI' else metric
    if function == 'general_benchmark_question':
        return general_benchmark_question(dfs, group, metric, limit)
    if function == 'general_benchmark_question_specific_segment':
        return general_benchmark_question_specific_segment(dfs, group, metric, limit, segment)
    elif function == 'opportunities_to_grow':
        return opportunities_to_grow(dfs, group, metric, ordering_type, limit)
    elif function == 'my_own_stats':
        return my_own_stats(dfs, group, metric, limit)
    elif function == 'compare_with_benchmark':
        return compare_with_benchmark(dfs, group, metric, limit)
    elif function == "my_data_interpret":
        return my_data_interpret(dfs)
    elif function == "my_trends":
        return my_trends(dfs, limit)
    elif function == 'benchmark_analyze':
        return benchmark_analyze(dfs, metric, limit)
    return json.dumps({"insight": f"Sorry, no insight to show"})


def calculate_price(response, model_used):
    input_token_count = response.usage.prompt_tokens
    output_token_count = response.usage.completion_tokens
    input_cost = (input_token_count / 1000) * token_prices[model_used]["input"]
    output_cost = (output_token_count / 1000) * token_prices[model_used]["output"]
    total_cost = round(input_cost + output_cost, 4)
    return total_cost


def roles_tracking(messages):
    roles_tracking = []
    for message in messages:
        if isinstance(message, dict) and "role" in message:
            roles_tracking.append(message["role"])
        elif hasattr(message, 'role'):
            roles_tracking.append(message.role)
    return roles_tracking
