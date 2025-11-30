"""
Tests for graph.py workflow
Goal: Ensure workflow graph builds and executes correctly with mocks.
"""

import pytest
from langgraph.graph import StateGraph, END
from langchain_core.messages import AIMessage

# Import your module
from app.agent.graph import research


# ===========================================
# MOCKS
# ===========================================

class MockLLM:
    """Mock LLM — produces predictable output without external API."""
    def invoke(self, messages):
        return AIMessage(content="mock-response")

    def bind_tools(self, tools):
        return self


class MockTool:
    name = "mock_tool"

    def invoke(self, q):
        return "mock tool result"


@pytest.fixture
def mock_state():
    return {
        "messages": [],
        "query": "Test query",
        "research_data": "",
        "verified_facts": "",
        "final_report": "",
        "iteration": 0,
        "max_iterations": 1,
        "fact_check_iteration": 0,
        "max_fact_check_iterations": 1
    }


# ===========================================
# BASIC GRAPH BUILD TEST
# ===========================================

def test_graph_build():
    """Ensure workflow graph builds successfully."""
    from app.agent.graph import workflow

    assert isinstance(workflow, StateGraph)

    # Check nodes exist
    nodes = workflow.nodes.keys()

    assert "researcher" in nodes
    assert "fact_checker" in nodes
    assert "summarizer" in nodes
    assert "tools" in nodes
    assert "save_research" in nodes
    assert "save_facts" in nodes


def test_graph_compile():
    """Ensure graph compiles without failing."""
    from app.agent.graph import workflow
    compiled = workflow.compile()
    assert compiled is not None


# ===========================================
# TEST EXECUTION THROUGH MOCKS
# ===========================================

def test_research_function_runs(monkeypatch):
    """Test that research() executes with mocks replacing LLM and tools."""

    # --- Patch LLM ---
    from app.agent import graph as g
    g.llm = MockLLM()

    # --- Patch Agents to use MockLLM ---
    g.researcher.llm = MockLLM()
    g.fact_checker.llm = MockLLM()
    g.summarizer.llm = MockLLM()

    # --- Patch tools ---
    g.my_tools[:] = [MockTool()]

    # Run research flow
    result = g.research("mock topic")

    # Basic result validations
    assert isinstance(result, dict)
    assert "final_report" in result
    assert isinstance(result["final_report"], str)


def test_research_state_structure(mock_state):
    """Ensure state fields exist after running agent graph."""
    from app.agent.graph import agent

    out = agent.invoke(mock_state)

    assert "query" in out
    assert "messages" in out
    assert "iteration" in out
    assert "fact_check_iteration" in out


def test_final_report_non_empty():
    """Ensure final report is not empty when research() completes."""
    from app.agent import graph as g

    # Patch LLM to avoid external call
    g.llm = MockLLM()
    g.researcher.llm = MockLLM()
    g.fact_checker.llm = MockLLM()
    g.summarizer.llm = MockLLM()

    res = g.research("AI and Python", max_iterations=1)

    assert isinstance(res["final_report"], str)
    assert len(res["final_report"]) > 0
