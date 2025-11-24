"""
Graph Module - Builds and manages the workflow
Purpose: Main orchestration logic
"""

from langgraph.graph import StateGraph,END
from langgraph.prebuilt import ToolNode
from langchain_groq import ChatGroq

# my project files 
from app.agent.state import MultiAgentState
from app.agent.tools import ResearchTools
from app.agent.agents import ResearcherAgent,FactCheckerAgent,SummarizerAgent
from app.agent.router import (
    should_continue_research,
    should_continue_fact_checking,
    after_tools,
    save_research_data,
    save_verified_facts
)
from app.agent.tools import my_tools
from dotenv import load_dotenv
load_dotenv()
# ===== BUILD WORKFLOW =====

# Initialize components
llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0.7)
researcher = ResearcherAgent(llm, my_tools)
fact_checker = FactCheckerAgent(llm, my_tools)
summarizer = SummarizerAgent(llm)
tool_node = ToolNode(my_tools)

# Build graph
workflow = StateGraph(MultiAgentState)

# Add nodes
workflow.add_node("researcher", researcher)
workflow.add_node("fact_checker", fact_checker)
workflow.add_node("summarizer", summarizer)
workflow.add_node("tools", tool_node)
workflow.add_node("save_research", save_research_data)
workflow.add_node("save_facts", save_verified_facts)

# Set entry point
workflow.set_entry_point("researcher")

# Researcher flow
workflow.add_conditional_edges(
    "researcher",
    should_continue_research,
    {
        "tools": "tools",
        "researcher": "researcher",
        "save_research": "save_research"  # FIXED
    }
)

workflow.add_edge("save_research", "fact_checker")

# Fact-checker flow
workflow.add_conditional_edges(
    "fact_checker",
    should_continue_fact_checking,
    {
        "tools": "tools",
        "save_facts": "save_facts"
    }
)

workflow.add_edge("save_facts", "summarizer")
workflow.add_edge("summarizer", END)

# Tools routing
workflow.add_conditional_edges(
    "tools",
    after_tools,
    {
        "researcher": "researcher",
        "fact_checker": "fact_checker",
        "save_research": "save_research"
    }
)

agent = workflow.compile()

# ===== EXECUTE =====

def research(query: str):
    initial_state = {
        "messages": [],
        "query": query,
        "research_data": "",
        "verified_facts": "",
        "final_report": "",
        "iteration": 0,
        "max_iterations": 2,
        "fact_check_iteration": 0,  # CRITICAL
        "max_fact_check_iterations": 1  # CRITICAL: Limit to 1 iteration
    }
    
    print("="*80)
    print("🚀 Starting Multi-Agent Research System")
    print("="*80)
    
    result = agent.invoke(initial_state)
    
    print("\n" + "="*80)
    print("📊 FINAL REPORT")
    print("="*80)
    print(result.get("final_report", "No report generated"))
    return result
