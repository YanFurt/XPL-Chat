from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.types import interrupt
from classes import State

@tool
def human_assistance(query: str) -> str:
    """If a team name is not recognised, use this tool to ask the user if they would like to update their query"""
    human_response = interrupt({"query": query})
    return human_response["data"]

tool_node = ToolNode(tools=[human_assistance])

def route_tools(
    state: State,
):
    """
    Use in the conditional_edge to route to the ToolNode if the last message
    has tool calls. Otherwise, route to the end.
    """
    if isinstance(state, list):
        ai_message = state[-1]
    elif messages := state.get("messages", []):
        ai_message = messages[-1]
    else:
        return "dummy_node2"
    if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
        return "tools"
    return "dummy_node2"