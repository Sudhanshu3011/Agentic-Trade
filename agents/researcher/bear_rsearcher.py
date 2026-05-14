import textwrap
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import StrOutputParser
from agents.base.base_researcher import BaseResearcher


class BearResearcher(BaseResearcher):

    def build_prompt(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a professional bearish equity analyst. Your goal is to dismantle "
                    "the investment case for a given stock. Maintain a skeptical, sharp, and "
                    "conversational tone, directly challenging bullish assumptions.\n\n"
                    "Focus on the following pillars in your analysis:\n"
                    "1. RISKS & CHALLENGES: Identify market saturation, financial instability, "
                    "or macroeconomic headwinds.\n"
                    "2. COMPETITIVE WEAKNESSES: Highlight declining innovation, eroding moats, "
                    "or superior rival positioning.\n"
                    "3. NEGATIVE INDICATORS: Support your claims with specific financial data, "
                    "technical trends, sector decline impact, or recent adverse news.\n"
                    "4. BULL COUNTERPOINTS: Critically analyze and expose over-optimistic "
                    "assumptions in the bullish thesis with sound reasoning.\n\n"
                    "Strategy: Don't just list facts. Engage in a debate, address the bull's "
                    "points directly, and emphasize potential downsides.",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

    def __init__(self):
        super().__init__()  # sets self.llm and self.prompt via build_prompt()
        self.chain = self.prompt | self.llm | StrOutputParser()

    def _build_input(self, state: dict) -> dict:
        ctx = self._unpack_debate(state)
        content = f"""
Company : {ctx['ticker']} | Sector: {ctx['sector']} | Round: {ctx['rounds']}

Analyst Reports
{ctx['report']}

Bull Thesis to Rebut
{ctx['bull_thesis']}

Debate History
{ctx['debate_history']}

Task: Build the strongest possible bear thesis.
Directly rebut the bull argument above.
        """.strip()

        return {"messages": [HumanMessage(content=content)]}

    def run(self, state: dict) -> str:
        return self.chain.invoke(self._build_input(state))
