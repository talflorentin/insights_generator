from utils import *
import logging


def run_conversation(dfs, client, query, messages=None):
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

    tool_calls = response_message.tool_calls
    if tool_calls:
        messages_branch = messages.copy()
        messages_branch.append(response_message)
        logging.info(f'\nChosen tools to use: {[tool.function.name for tool in tool_calls]}')
        available_functions = {"get_answer_to_ua_question": get_answer_to_ua_question}
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            logging.info(f'\nFunction args detects: {function_args}')
            function_response = function_to_call(
                dfs=dfs,
                function=function_args.get("function"),
                metric=function_args.get("metric"),
                group=function_args.get("group"),
                ordering_type=function_args.get("ordering_type", 'total_installs'),
                limit=function_args.get("limit", 5),
                segment=function_args.get("segment", None),
            )

            messages_branch.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                }
            )
        messages_branch.append({"role": "system", "content": "Show the results, along with suggestion for 3 follow-up questions:\
        If your results contain '_int', keep it. For cost and revenue numbers, add $ sign. For retention rates and rate differences add % sign.\
        if the result for the question is not within the JSON, say you don't have the answer at the moment, do not come up with a fake answer!\
        If possible, show the results as a table.\
        If user asked to interpret his data, don't show all the results, just create some interesting and meaningful insights.\
        The follow up questions should be in the same 'style' but not a copy of the previous questions.\
        they should not contain actual names of countries or media sources."})
        second_response = client.chat.completions.create(
            model=model_to_use,
            messages=messages_branch,
            temperature=0
        )
        llm_price_second = calculate_price(second_response, model_to_use)
        llm_price_all = round(llm_price_first + llm_price_second, 4)
        logging.info(f'LLM Price all: {llm_price_all}$')

        second_response_message = second_response.choices[0].message
        messages.append(second_response_message)
        response_message_text = second_response_message.content
        logging.info(f'Roles in branch conversation: {roles_tracking(messages_branch)}')
    else:
        messages.append(response_message)
        logging.info(f'\nNo tools chosen!')
        response_message_text = response_message.content

    logging.info(f'Roles in conversation: {roles_tracking(messages)}')
    return response_message_text, messages
