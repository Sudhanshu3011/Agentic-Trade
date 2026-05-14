from graph.state import AgentState
from agents.analysis.market_analyst import MarketAnalyst
from agents.analysis.news_analyst import NewsAnalyst
from agents.analysis.sector_analyst import SectorAnalyst
from agents.analysis.technical_analyst import TechnicalAnalyst
from agents.analysis.fundamental_analyst import FundamentalAnalyst
from agents.researcher.bull_researcher import BullResearcher
from agents.researcher.bear_rsearcher import BearResearcher
from agents.manager.research_manager import ResearchManager
from core.error import handle_node_errors, validate_state
from core.logging import get_logger
import time

logger = get_logger(__name__)


market_analyst = MarketAnalyst()
fundamental_analyst = FundamentalAnalyst()
technical_analyst = TechnicalAnalyst()
news_analyst = NewsAnalyst()
sector_analyst = SectorAnalyst()
bull_researcher = BullResearcher()
bear_researcher = BearResearcher()
research_manager = ResearchManager()


@handle_node_errors("market_analyst")
def run_market_analyst(state: AgentState) -> dict:
    market_report = market_analyst.run()
    return {"market_analyst_report": market_report}


@handle_node_errors("fundamental_analyst")
def run_fundamental_analyst(state: AgentState) -> dict:
    time.sleep(
        1.5
    )  # intentional delay to reduce likelihood of yfinance.info 401 errors
    fundamental_report = fundamental_analyst.run(state)
    return {"fundamental_analyst_report": fundamental_report}


@handle_node_errors("technical_analyst")
def run_technical_analyst(state: AgentState) -> dict:
    technical_report = technical_analyst.run(state)
    return {"technical_analyst_report": technical_report}


@handle_node_errors("news_analyst")
def run_news_analyst(state: AgentState) -> dict:
    news_report = news_analyst.run(state)
    return {"news_analyst_report": news_report}


@handle_node_errors("sector_analyst")
def run_sector_analyst(state: AgentState) -> dict:
    sector_report = sector_analyst.run(state)
    return {"sector_analyst_report": sector_report}


@handle_node_errors("bull_researcher")
def run_bull_researcher(state: AgentState) -> dict:
    time.sleep(60)
    bull_thesis = bull_researcher.run(state)

    debate = state.get("investment_debate", {})
    rounds = debate.get("debate_rounds", 0)
    history = debate.get("debate_history", "")
    speaker_history = debate.get("speaker_history", [])

    updated_history = history + f"\n\n[Round {rounds + 1}] BULL:\n{bull_thesis}"

    return {
        "investment_debate": {
            **debate,
            "bull_thesis": bull_thesis,
            "debate_history": updated_history,
            "debate_rounds": rounds + 1,
            "last_speaker": "bull",
            "speaker_history": speaker_history + ["bull"],
        }
    }


@handle_node_errors("bear_researcher")
def run_bear_researcher(state: AgentState) -> dict:
    time.sleep(60)
    bear_thesis = bear_researcher.run(state)

    debate = state.get("investment_debate", {})
    rounds = debate.get("debate_rounds", 0)
    history = debate.get("debate_history", "")
    speaker_history = debate.get("speaker_history", [])

    updated_history = history + f"\n\n[Round {rounds}] BEAR:\n{bear_thesis}"

    return {
        "investment_debate": {
            **debate,
            "bear_thesis": bear_thesis,
            "debate_history": updated_history,
            "debate_rounds": rounds + 1,
            "last_speaker": "bear",
            "speaker_history": speaker_history + ["bear"],
        }
    }


@handle_node_errors("research_manager")
def run_research_manager(state: AgentState) -> dict:
    time.sleep(60)
    verdict = research_manager.run(state)

    debate = state.get("investment_debate", {})
    speaker_history = debate.get("speaker_history", [])

    return {
        "research_verdict": verdict,
        "investment_debate": {
            **debate,
            "final_decision": verdict,
            "last_speaker": "manager",
            "speaker_history": speaker_history + ["manager"],
        },
    }
