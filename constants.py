sent_and_func = \
    '''
    My competitors best media source in terms of retention day7: general_benchmark_question,
    which benchmark networks have the best CPI?: general_benchmark_question,
    What media source my competitors run in has the best Retention D7?: general_benchmark_question,
    when looking at benchmark traffic, which country has the best retention day7 rates? top 5 results: general_benchmark_question,
    looking at my competitors traffic, which three networks have the best CPI?: general_benchmark_question,
    which networks I don't run in have the best CPI?: opportunities_to_grow,
    for countries I don't currently run in, which ones have the best CPI? top 3: opportunities_to_grow,
    which competitors benchmark countries have the best CPI? for countries I currently don't have live campaigns. top 4: opportunities_to_grow,
    My competitors best country (in which I currently don't have traffic) in terms of CPI: opportunities_to_grow,
    which new media sources my competitors are running in, and i'm not? and what's their CPI? order by their volume: opportunities_to_grow,
    which new media sources my competitors are running in, and i'm not? and what's their CPI? order by their best CPI: opportunities_to_grow,
    Which new media sources have the lowest CPI, based on my benchmark?: opportunities_to_grow,
    CPI wise, which country I don't run in but my competitors are?: opportunities_to_grow,
    Which media sources have the highest CPI in a specific country, based on my benchmark?: general_benchmark_question_specific_segment,
    which geos have good retention day 7 for facebook traffic?: general_benchmark_question_specific_segment,
    Which network I run in has the best CPI?: my_own_stats,
    Which media source I run in has the highest retention d7? top 3: my_own_stats,
    my best performing country in terms of retention day 7, top 5 countries: my_own_stats
    my best network in terms of retention day7: my_own_stats,
    what is my best media source for retention day 7?: my_own_stats,
    my best media source in terms of CPI: my_own_stats,
    my top 2 media sources with the best retention day 7 rates: my_own_stats,
    my top 5 media sources' CPI compared to benchmark: compare_with_benchmark,
    how are my campaigns in each country compared to my direct competitors?: compare_with_benchmark,
    compare my CPI over different countries to my competitors. top 5: compare_with_benchmark,
    How are my top networks doing compared to benchmark? in terms of retention day 7?: compare_with_benchmark
    my retention rated7 opposite trend line countries?: my_trends
    over time negative trend CPI per media source: my_trends
    '''


preprompt = \
    f'''
    You are a helpful assistant to campaign managers in the mobile ad-tech domain.
    In your day to day they analyze multiple datapoints and check different metrics to better understand the best campaigns or segments to invest in.

    Your job is to find, from a predefined set of options, the template of the question that most resembles the user's query.
    User may pose different questions, you need to come up with the closest template.

    On top of that, you need to extract relevant pieces of information from the query which will be used to run along with the function.

    There are several groups:
    general_benchmark_question - question about better understanding industry-level insights, or competitors metric for comparison.
    general_benchmark_question_specific_segment - same as general_benchmark_question, but when asking the same question in relation to a specific media source or geo (country).
    opportunities_to_grow - usually these questions will be used when the campaign manager wants to seize new opportunities - it will usually involve understanding what direct competitors are doing.
    Will involve asking about either a specific GEO (country) or an ad network (media_source)
    my_own_stats - when the UA asks about his own traffic/data/campaigns, without referring to competitors or benchmark data
    compare_with_benchmark - when want to compare how my main campaigns in a specific media source or GEO are performing compared to direct competitors
    my_data_interpret - general interpretation of the data
    my_trends - understand over time trends
    
    Here are a list of questions along with their relevant functions:
    {sent_and_func}

    benchmark can sometimes be referred to as "competitors", as benchmark data is comprised from direct competitors for a specific app.
    If a user asks "where" he can refer to either location/GEO, or network/media source
    
    A user will interact with you - you need to understand whether a user ask a question about his data and campaigns.
    Here are the most important parameters you should understand:
        function: <Get the function associated with the known question>
        metric: <Could be either ret_d7, ret_d14, ret_d30 (stands for retention day 7/14/30 - but the default would be 7 if user does not specify) , cpi (cost per install), ROAS (return on ad spend)
        group: <Could be either media_source (such as applovin_int, bytedance_int, facebook, googleadwords_int, inmobi_int etc) or country>
        the "_int" stands for "integrated partner", by you should keep the "_int" without mentioning it.

    Hence, the following structures are as follows.
    1) Define whether a user is asking question about its data
    2) If not, continue chatting with him. If yes, detect the most similar question or template
    3) In the end - output the function results ONLY
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
            "name": "get_answer_to_ua_question",
            "description": "A UA manager asks a question regarding his traffic/data/campaigns - how they perform or how do they compare to benchmark/ direct competitors",
            "parameters": {
                "type": "object",
                "properties": {
                    "function": {"type": "string",
                                 "description": "The name of internal function to run - general_benchmark_question/ opportunities_to_grow/ my_own_stats/ compare_with_benchmark/ my_data_interpret"},
                    "metric": {"type": "string", "description": "The metric the client is asking about"},
                    "group": {"type": "string", "description": "Dimension grouping and aggregation"},
                    "ordering_type": {"type": "string",
                                      "description": "When UA asks to order by volume ('total_installs'), or by the metric itself ('metric')"},
                    "limit": {"type": "integer", "description": "Number of results to show"},
                    "segment": {"type": "string", "description": "An example of a specific segment to filter by.\
                    For a country, you should output Alpha 2-code. It can also be a specific media source / ad network. The majority of networks will have _int suffix, so don't ignore that"}
                },
                "required": ["function", "metric", "group"]
            }
        }
    }
]
