preprompt = \
    f'''
    You are a helpful assistant to campaign managers in the mobile ad-tech domain.
    In your day to day they analyze multiple datapoints and check different metrics to better understand the best campaigns or segments to invest in.

    The UA will ask you questions about his data and will oftentimes want to compare it to benchmark data.
    Benchmark can sometimes be referred to as "competitors", as benchmark data is comprised from direct competitors for a specific app.
    If a user asks "where" he can refer to either location/GEO, or network/media source
    
    A user will interact with you - you need to understand whether a user ask a question about his data and campaigns.
    Here are the most important parameters you should understand:
        metric: <Could be either ret_d7, ret_d14, ret_d30 (stands for retention day 7/14/30 - but the default would be 7 if user does not specify) , cpi (cost per install), ROAS (return on ad spend)>
        group: <Could be either media_source (such as applovin_int, bytedance_int, facebook, googleadwords_int, inmobi_int etc) or country>
        the "_int" stands for "integrated partner", by you should keep the "_int" without mentioning it.

    Hence, the following structures are as follows.
    1) Define whether a user is asking question about its data
    2) If not, continue chatting with him. If yes, detect the most similar question or template
    3) In the end - output the function results with some explanation
    '''

# model_to_use = "gpt-4-1106-preview"
model_to_use = "gpt-3.5-turbo-1106"

token_prices = {
    "gpt-4-1106-preview": {"input": 0.01, "output": 0.03},
    "gpt-3.5-turbo-1106": {"input": 0.001, "output": 0.002}
}

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_answer_about_my_data",
            "description": "A UA manager asks a question regarding competitors/benchmark traffic/data/campaigns",
            "parameters": {
                "type": "object",
                "properties": {
                    "metric": {"type": "string", "description": "The metric the client is asking about"},
                    "group": {"type": "string", "description": "Dimension grouping and aggregation"},
                    "ordering_type": {"type": "string", "description": "When UA asks to order by volume ('total_installs'), or by the metric itself ('metric')"},
                    "limit": {"type": "integer", "description": "Number of results to show"},
                    "filter": {"type": "string", "description": "Filter a for a specific media_source or country. For example (media_source, facebook), (country, UK)"}
                },
                "required": ["metric", "group"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "get_answer_about_benchmark_data",
            "description": "A UA manager asks a question regarding competitors/benchmark traffic/data/campaigns",
            "parameters": {
                "type": "object",
                "properties": {
                    "metric": {"type": "string", "description": "The metric the client is asking about"},
                    "group": {"type": "string", "description": "Dimension grouping and aggregation"},
                    "ordering_type": {"type": "string", "description": "When UA asks to order by volume ('total_installs'), or by the metric itself ('metric')"},
                    "limit": {"type": "integer", "description": "Number of results to show"},
                    "filter": {"type": "string", "description": "Filter a for a specific media_source or country. For example (media_source, facebook), (country, UK)"}
                },
                "required": ["metric", "group"]
            }
        }
    },
]
