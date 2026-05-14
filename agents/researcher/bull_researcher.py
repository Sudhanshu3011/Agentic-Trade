import textwrap
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import StrOutputParser
from agents.base.base_researcher import BaseResearcher


class BullResearcher(BaseResearcher):

    def build_prompt(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a professional bullish equity analyst. Your goal is to build a "
                    "compelling investment case for the stock, emphasizing its upside and resilience.\n\n"
                    "YOUR TASK:\n"
                    "- Identify and articulate exactly 3 strong, distinct reasons why this stock "
                    "is a 'Buy' or 'Outperform'.\n"
                    "- GROWTH POTENTIAL: Highlight market opportunities, revenue scalability, "
                    "and long-term projections.\n"
                    "- COMPETITIVE ADVANTAGES: Showcase unique products, strong branding, "
                    "or a dominant market moat.\n"
                    "- POSITIVE INDICATORS: Support your thesis with strong financial health, "
                    "favorable industry trends, and recent catalysts.\n"
                    "- BEAR COUNTERPOINTS: Address common skeptical arguments directly, using "
                    "data to show why the bear case is overblown or shortsighted.\n\n"
                    "TONE & STYLE:\n"
                    "Be confident, visionary, and persuasive. Engage in a conversational debate "
                    "with the bear analyst, directly countering their pessimism with sound "
                    "reasoning and data-driven optimism.",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

    def __init__(self):
        super().__init__()  # sets self.llm and self.prompt via build_prompt()
        self.chain = self.prompt | self.llm | StrOutputParser()

    #     def _build_input(self, state: dict) -> dict:
    #         ctx = self._unpack_debate(state)
    #         content = f"""
    # Company: {ctx['ticker']} | Sector: {ctx['sector']} | Round: {ctx['rounds']}

    # Analyst Reports
    # {ctx['report']}

    # Bear Thesis to Rebut
    # {ctx['bear_thesis']}

    # Debate History
    # {ctx['debate_history']}

    # Task: Build the strongest possible bull thesis.
    # Directly rebut the bear argument above if None yet than no rebuttal needed.
    #         """.strip()

    #         return {"messages": [HumanMessage(content=content)]}

    def _build_input(self, state: dict) -> dict:

        ctx = self._unpack_debate(state)
        bear_section = ""
        debate_section = ""

        if ctx["bear_thesis"] != "None yet.":
            bear_section = f"""
                    Bear Thesis to Rebut
                    {ctx['bear_thesis']}
                """

        if ctx["debate_history"] != "No prior debate.":
            debate_section = f"""
                Debate History
                {ctx['debate_history']}
                """

        content = f"""
Company: {ctx['ticker']} | Sector: {ctx['sector']} | Round: {ctx['rounds']}

Analyst Reports
{ctx['report']}

{bear_section}

{debate_section}

Task:
Build the strongest possible bull thesis.
""".strip()

        return {"messages": [HumanMessage(content=content)]}

    def run(self, state: dict) -> str:
        return self.chain.invoke(self._build_input(state))
