import textwrap
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage
from pydantic import BaseModel
from typing import Literal
from agents.base.base_researcher import BaseResearcher


class Verdict(BaseModel):
    decision: Literal["BUY", "SELL", "HOLD"]
    rationale: str
    strategy: str


class ResearchManager(BaseResearcher):
    """
    Reads the completed debate and delivers a structured verdict.
    Uses with_structured_output so trade_signal maps directly to AgentState.
    """

    def build_prompt(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a senior research manager and the final decision-maker in an "
                    "investment debate. You have reviewed arguments from both a bull and a "
                    "bear analyst.\n\n"
                    "YOUR TASK:\n"
                    "- Objectively weigh the bull and bear theses against the analyst reports.\n"
                    "- Identify which side presented stronger, data-backed reasoning.\n"
                    "- Deliver a final verdict: BUY, SELL, or HOLD.\n"
                    "- Provide a clear rationale explaining why one side prevailed.\n"
                    "- Outline a concise investment strategy based on your decision.\n\n"
                    "TONE & STYLE:\n"
                    "Be decisive, neutral, and analytical. Avoid being swayed by confidence "
                    "alone — prioritize evidence and risk-adjusted reasoning.",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

    def __init__(self):
        super().__init__()  # sets self.llm and self.prompt via build_prompt()
        self.chain = self.prompt | self.llm.with_structured_output(Verdict)

    def _build_input(self, state: dict) -> dict:
        ctx = self._unpack_debate(state)
        content = f"""
Company: {ctx['ticker']} | Sector: {ctx['sector']}
Debate rounds completed: {ctx['rounds']}

Bull Thesis 
{ctx['bull_thesis']}

Bear Thesis
{ctx['bear_thesis']}

Full Debate History
{ctx['debate_history']}

Weigh both sides. Deliver your final verdict as BUY, SELL, or HOLD
with clear rationale and a concise investment strategy.
        """

        return {"messages": [HumanMessage(content=content)]}

    def run(self, state: dict) -> Verdict:
        return self.chain.invoke(self._build_input(state))
