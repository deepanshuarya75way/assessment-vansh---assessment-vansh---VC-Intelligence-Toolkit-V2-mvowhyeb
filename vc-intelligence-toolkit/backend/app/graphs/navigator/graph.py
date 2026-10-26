from langgraph.graph import END, START, StateGraph

from app.graphs.navigator.nodes import (
    application_parsing_node,
    confidence_node,
    evaluate_fit_node,
    formatter_node,
    interview_question_node,
    retrieve_context_node,
)
from app.graphs.navigator.state import NavigatorState

builder = StateGraph(NavigatorState)

builder.add_node("application_parsing", application_parsing_node)
builder.add_node("retrieve_context", retrieve_context_node)
builder.add_node("evaluate_fit", evaluate_fit_node)
builder.add_node("confidence", confidence_node)
builder.add_node("interview_questions", interview_question_node)
builder.add_node("formatter", formatter_node)

builder.add_edge(START, "application_parsing")
builder.add_edge("application_parsing", "retrieve_context")
builder.add_edge("retrieve_context", "evaluate_fit")
builder.add_edge("evaluate_fit", "confidence")
builder.add_edge("confidence", "interview_questions")
builder.add_edge("interview_questions", "formatter")
builder.add_edge("formatter", END)

navigator_graph = builder.compile()
