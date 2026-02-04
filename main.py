from langgraph.graph import StateGraph, START, END
from nodes import get_collections,get_fields,get_filters,dummy_node,get_response,fetch_data,route1,get_agg
from classes import State
from langgraph.checkpoint.memory import InMemorySaver
from tools import tool_node,route_tools
from langgraph.types import Command
from dotenv import load_dotenv
from pymongo import MongoClient
import os
load_dotenv()

client = MongoClient(os.getenv("MONGO"))
database = client.XPL_2025_db


memory = InMemorySaver()
graph_builder = StateGraph(State)
graph_builder.add_node("table", get_collections)
graph_builder.add_node("get_filters",get_filters)
graph_builder.add_node("get_fields",get_fields)
graph_builder.add_node("fetch_data",fetch_data,defer=True)
graph_builder.add_node("get_response",get_response)
graph_builder.add_node("dummy_node1",dummy_node)
graph_builder.add_node("dummy_node2",dummy_node)
graph_builder.add_node("tools", tool_node)

                       
graph_builder.add_edge(START, "table")
graph_builder.add_conditional_edges("table", route1, ['get_response','dummy_node1'])
graph_builder.add_edge("dummy_node1","get_filters")
graph_builder.add_edge("dummy_node1","get_fields")
graph_builder.add_conditional_edges("get_filters",route_tools,["tools","dummy_node2"])
graph_builder.add_edge("tools","get_filters")
#graph_builder.add_edge("get_filters","get_fields")
graph_builder.add_edge(['get_fields','dummy_node2'],'fetch_data')
#graph_builder.add_edge('get_fields','fetch_data')
graph_builder.add_edge('fetch_data','get_response')
graph_builder.add_edge('get_response',END)
graph = graph_builder.compile(checkpointer=memory)

print('Ask me anything about XPL 2025')
config = {"configurable": {"thread_id": "1","database":database}}
while True:
    query=input('User: ')
    if query in ['q','exit']:
        break
    events = graph.stream(
        {"userquery":query},
        config,
        stream_mode="values",
        )
    for event in events:
        #print(event)
        if 'response' in event:
            print('AI: ', end='')
            print(event["response"])
    if ms:=event['messages']:
        aim = ms[-1].tool_calls[0]['args']['query']
        print('AI: ',aim)
        inp=input()
        events2 = graph.stream(
        Command(resume={"data":inp}),
        config,
        stream_mode="values",
            )
        for event in events2:
                #print(event)
                if 'response' in event:
                    print(event["response"])
        