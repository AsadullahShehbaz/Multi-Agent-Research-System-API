
"""
Tests for all agents: Researcher, FactChecker, Summarizer
"""

import pytest
from langchain_core.messages import AIMessage, ToolMessage

from app.agent.agents import ResearcherAgent, FactCheckerAgent, SummarizerAgent
from app.agent.state import MultiAgentState


# =============================================
# MOCK LLM
# =============================================

class MockLLM:
    """Simple mock LLM to simulate stable responses."""

    def __init__(self, return_tool_call=False):
        self.return_tool_call = return_tool_call

    def invoke(self, messages):
        """Simulate LLM output."""
        if self.return_tool_call:
            return AIMessage(
                content="Mock tool call result.",
                tool_calls=[
                    {
                        "id": "call_1",
                        "name": "google_web_search",
                        "args": {"query": "AI"},
                        "type": "tool_call",
                    }
                ],
            )
        return AIMessage(content="Mock LLM response")

    def bind_tools(self, tools):
        """Return self since we don’t execute real tools."""
        return self


# =============================================
# FIXTURES
# =============================================

@pytest.fixture
def base_state() -> MultiAgentState:
    return {
        "messages": [],
        "query": "What is AI?",
        "research_data": "",
        "verified_facts": "",
        "final_report": "",
        "iteration": 0,
        "max_iterations": 2,
        "fact_check_iteration": 0,
        "fact_check_max_iterations": 1
    }


@pytest.fixture
def simple_tool():
    class T:
        name = "web_search"
        def invoke(self, x): return "search results"
    return [T()]


# =============================================
# TEST ResearcherAgent
# =============================================

def test_researcher_first_iteration(base_state, simple_tool):
    llm = MockLLM(return_tool_call=True)
    agent = ResearcherAgent(llm, simple_tool)

    output = agent(base_state)

    assert "messages" in output
    assert output["iteration"] == 1
    assert len(output["messages"]) == 1

    msg = output["messages"][0]
    assert isinstance(msg, AIMessage)
    assert msg.tool_calls is not None
    assert msg.tool_calls[0]["name"] == "google_web_search"


def test_researcher_second_iteration(base_state, simple_tool):
    llm = MockLLM()
    agent = ResearcherAgent(llm, simple_tool)

    # Add previous tool message
    base_state["messages"] = [ToolMessage(content="old result", tool_call_id="1")]

    output = agent(base_state)

    assert output["iteration"] == 1
    assert isinstance(output["messages"][0], AIMessage)
    assert "Mock LLM response" in output["messages"][0].content


# =============================================
# TEST FactCheckerAgent
# =============================================

def test_fact_checker_uses_research_data(base_state, simple_tool):
    llm = MockLLM()
    agent = FactCheckerAgent(llm, simple_tool)

    base_state["research_data"] = "This is test research data..."

    output = agent(base_state)

    assert output["fact_check_iteration"] == 1
    assert isinstance(output["messages"][0], AIMessage)


def test_fact_checker_extracts_from_tool_messages(base_state, simple_tool):
    llm = MockLLM()
    agent = FactCheckerAgent(llm, simple_tool)

    # Empty research_data → should fallback
    base_state["messages"] = [
        ToolMessage(content="tool result 1", tool_call_id="x"),
        ToolMessage(content="tool result 2", tool_call_id="y"),
    ]

    output = agent(base_state)

    assert output["fact_check_iteration"] == 1
    assert isinstance(output["messages"][0], AIMessage)


def test_fact_checker_tool_call(base_state, simple_tool):
    llm = MockLLM(return_tool_call=True)
    agent = FactCheckerAgent(llm, simple_tool)

    output = agent(base_state)

    msg = output["messages"][0]
    assert msg.tool_calls is not None
    assert msg.tool_calls[0]["name"] == "google_web_search"


# =============================================
# TEST SummarizerAgent
# =============================================

def test_summarizer_produces_report(base_state):
    llm = MockLLM()
    agent = SummarizerAgent(llm)

    base_state["research_data"] = "AI is intelligence..."
    base_state["verified_facts"] = "AI is used in ML..."

    output = agent(base_state)

    assert "final_report" in output
    assert isinstance(output["messages"][0], AIMessage)
    assert len(output["final_report"]) > 0
    assert "Mock LLM response" in output["final_report"]
