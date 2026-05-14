from abc import ABC, abstractmethod
from typing import Any
from langchain_core.prompts import ChatPromptTemplate
from config.settings import get_llm


class BaseResearcher(ABC):
    """
    Base for all debate-layer agents (bull, bear, research manager).
    Handles state unpacking. Each subclass defines its own prompt and run().
    """

    def __init__(self):
        self.llm = get_llm()
        self.prompt: ChatPromptTemplate = (
            self.build_prompt()
        )  # call it, don't assign it

    @abstractmethod
    def build_prompt(self) -> ChatPromptTemplate:
        """Return the ChatPromptTemplate for this researcher."""
        pass

    @abstractmethod
    def run(self, state: dict) -> Any:
        """Execute reasoning over AgentState and return result."""
        pass

    def _final_report(self, state: dict) -> str:
        return f"""
MARKET ANALYSIS:
{state.get('market_analyst_report', 'Not available')}

FUNDAMENTAL ANALYSIS:
{state.get('fundamental_analyst_report', 'Not available')}

TECHNICAL ANALYSIS:
{state.get('technical_analyst_report', 'Not available')}

NEWS ANALYSIS:
{state.get('news_analyst_report', 'Not available')}

SECTOR ANALYSIS:
{state.get('sector_analyst_report', 'Not available')}
""".strip()

    def _unpack_debate(self, state: dict) -> dict:
        debate = state.get("investment_debate", {})
        return {
            "ticker": state.get("ticker_of_company", ""),
            "sector": state.get("sector_of_company", ""),
            "report": self._final_report(state),
            "bull_thesis": debate.get("bull_thesis", "None yet."),
            "bear_thesis": debate.get("bear_thesis", "None yet."),
            "debate_history": debate.get("debate_history", "No prior debate."),
            "rounds": debate.get("debate_rounds", 0),
        }
