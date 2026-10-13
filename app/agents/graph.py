from langgraph.graph import StateGraph, END

from app.agents.state import AgentState
from app.agents.nodes import (
    intent_recognition_node,
    execute_tools_node,
    generate_answer_node,
    should_execute_tools,
)


def build_agent_graph():
    """构建 Agent 图"""
    workflow = StateGraph(AgentState)

    # 节点名不要和 state 字段名冲突
    workflow.add_node("recognize_intent", intent_recognition_node)
    workflow.add_node("execute_tools", execute_tools_node)
    workflow.add_node("generate_answer", generate_answer_node)

    workflow.set_entry_point("recognize_intent")

    workflow.add_conditional_edges(
        "recognize_intent",
        should_execute_tools,
        {
            "execute": "execute_tools",
            "generate": "generate_answer",
        },
    )

    workflow.add_edge("execute_tools", "generate_answer")
    workflow.add_edge("generate_answer", END)

    return workflow.compile()


agent_graph = build_agent_graph()