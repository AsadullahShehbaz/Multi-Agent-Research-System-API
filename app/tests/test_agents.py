"""
Tests Module - Unit tests for agents
Purpose: Ensure code quality and reliability
"""

import pytest
from agent.tools import ResearchTools
from agent.state import MultiAgentState
from agent.agents import ResearcherAgent, FactCheckerAgent, SummarizerAgent


def test_research_tools():
    """Test tools initialization"""
    tools = ResearchTools()
    tool_list = tools.get_tools()
    
    assert len(tool_list) == 3
    assert tool_list[0].name == "web_search"
    assert tool_list[1].name == "web_scrape"
    assert tool_list[2].name == "calculate"


def test_web_search():
    """Test web search tool"""
    tools = ResearchTools()
    result = tools.web_search("Python programming")
    
    assert isinstance(result, str)
    assert len(result) > 0


def test_calculate():
    """Test calculator tool"""
    tools = ResearchTools()
    result = tools.calculate("2 + 2")
    
    assert "4" in result


def test_state_structure():
    """Test state type definition"""
    state: MultiAgentState = {
        "messages": [],
        "query": "test",
        "research_data": "",
        "verified_facts": "",
        "final_report": "",
        "iteration": 0,
        "max_iterations": 2
    }
    
    assert state["query"] == "test"
    assert state["iteration"] == 0


# Run tests: pytest tests/test_agents.py -v