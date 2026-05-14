MAX_DEBATE_ROUNDS = 1


def should_continue_debate(state) -> str:
    debate = state.get("investment_debate", {})

    rounds = debate.get("debate_rounds", 0)
    last_speaker = debate.get("last_speaker", "")

    if rounds >= 2 * MAX_DEBATE_ROUNDS:
        return "research_manager"

    if last_speaker == "bull":
        return "bear_researcher"
    else:
        return "bull_researcher"
