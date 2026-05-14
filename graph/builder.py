from langgraph.graph import END, START, StateGraph
from graph.state import AgentState
import graph.nodes as nodes
import graph.conditional_edges as conditional_edges
from core.logging import get_logger

logger = get_logger(__name__)


def build_graph():

    work_flow = StateGraph(AgentState)

    work_flow.add_node("market_analyst", nodes.run_market_analyst)
    work_flow.add_node("technical_analyst", nodes.run_technical_analyst)
    work_flow.add_node("news_analyst", nodes.run_news_analyst)
    work_flow.add_node("fundamental_analyst", nodes.run_fundamental_analyst)
    work_flow.add_node("sector_analyst", nodes.run_sector_analyst)
    work_flow.add_node("bull_researcher", nodes.run_bull_researcher)
    work_flow.add_node("bear_researcher", nodes.run_bear_researcher)
    work_flow.add_node("research_manager", nodes.run_research_manager)

    for analyst in [
        "market_analyst",
        "fundamental_analyst",
        "technical_analyst",
        "news_analyst",
        "sector_analyst",
    ]:
        work_flow.add_edge(START, analyst)
        work_flow.add_edge(analyst, "bull_researcher")

    work_flow.add_conditional_edges(
        "bull_researcher",
        conditional_edges.should_continue_debate,
        {
            "bear_researcher": "bear_researcher",
            "research_manager": "research_manager",
        },
    )
    work_flow.add_conditional_edges(
        "bear_researcher",
        conditional_edges.should_continue_debate,
        {
            "bull_researcher": "bull_researcher",
            "research_manager": "research_manager",
        },
    )

    work_flow.add_edge("research_manager", END)

    return work_flow.compile(debug=True)


try:
    app = build_graph()

except Exception as e:

    raise RuntimeError(f"Graph validation failed: {e}")
