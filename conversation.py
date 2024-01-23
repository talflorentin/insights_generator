from utils import *
import logging


def run_conversation(dfs, client, query, messages=None, total_cost_so_far=0):
    if messages is None:
        messages = [{"role": "system", "content": preprompt},
                    {"role": "user", "content": query}]
    else:
        messages.append({"role": "user", "content": query})
    logging.info('Going to OpenAI....')
    response = client.chat.completions.create(
        model=model_to_use,
        messages=messages,
        tools=tools,
        tool_choice="auto",
        temperature=0
    )
    response_message = response.choices[0].message
    llm_price_first = calculate_price(response, model_to_use)
    if llm_price_first < 1:
        c = round(llm_price_first * 100, 2)
        logging.info(f'LLM First call: {c}c')
    else:
        logging.info(f'LLM First call: {round(llm_price_first, 4)}$')
    total_cost_so_far += llm_price_first

    tool_calls = response_message.tool_calls
    img = None
    function_response_text = None
    if tool_calls:
        messages_branch = messages.copy()
        messages_branch.append(response_message)
        logging.info(f'\nChosen tools to use: {[tool.function.name for tool in tool_calls]}')
        available_functions = {"get_answer_about_my_data": get_answer_about_my_data,
                               "get_answer_about_benchmark_data": get_answer_about_benchmark_data}
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            logging.info(f'\nFunction args detects: {function_args}')
            function_response = function_to_call(
                dfs=dfs,
                metric=function_args.get("metric"),
                group=function_args.get("group"),
                ordering_type=function_args.get("ordering_type", 'total_installs'),
                limit=function_args.get("limit", 5)
            )

            if isinstance(function_response, tuple):
                function_response_text = function_response[0]
                img = function_response[1]
            elif isinstance(function_response, str):
                function_response_text = function_response

            messages_branch.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response_text,
                }
            )

        messages_branch.append({"role": "system", "content": "Show the results, but make sure not to change any value and print it the way you see it\
        If your results contains values with suffix '_int', keep it - and make sure it's lowercase. For cost and revenue numbers, add $ sign. For retention rates and rate differences add % sign.\
        if the result for the question is not within the JSON, say you don't have the answer at the moment, do not come up with a fake answer!\
        If possible, show the results as a table. Don't skip any columns, show all of them.\
        If you get 2 tables, try to combine them to one, but rows should have the same keys"})

        second_response = client.chat.completions.create(
            model=model_to_use,
            messages=messages_branch,
            temperature=0
        )
        llm_price_second = calculate_price(second_response, model_to_use)
        total_cost_so_far += llm_price_second
        if llm_price_second < 1:
            c = round(llm_price_second * 100, 2)
            logging.info(f'LLM Second call: {c}c')
        else:
            logging.info(f'LLM Second call: {round(llm_price_second, 4)}$')

        second_response_message = second_response.choices[0].message
        messages.append(second_response_message)
        response_message_text = second_response_message.content
        logging.info(f'Roles in branch conversation: {roles_tracking(messages_branch)}')
    else:
        messages.append(response_message)
        logging.info(f'\nNo tools chosen!')
        response_message_text = response_message.content

    logging.info(f'Roles in conversation: {roles_tracking(messages)}')
    if total_cost_so_far < 1:
        c = round(total_cost_so_far * 100, 2)
        logging.info(f'Total cost so far: {c}c')
    else:
        logging.info(f'Total cost so far: {round(total_cost_so_far, 4)}$')
    return response_message_text, messages, img, total_cost_so_far
