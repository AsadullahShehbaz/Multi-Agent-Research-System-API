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

import os 
import logging
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)

class MultiAgentSystem:
    """
    Main Multi-Agent Research System
    
    Orchestrates multiple AI agents with tool access
    for comprehensive research workflows
    """
    def __init__(self,api_key:str=None):
        """
        Initialize the multi-agent system
        
        Args:
            api_key: Groq API key (optional, reads from env)
        """
        logger.info("Initializing Multi-Agent System")

        # 1.Initialize llm 
        self.llm = ChatGroq(
            model="openai/gpt-oss-120b",
            api_key=api_key or os.getenv("GROQ_API_KEY")
        )

        # 2.Initialize tools
        self.tool_manager = ResearchTools()
        self.tools = self.tool_manager.get_tools()

        # 3.Bind tools to llm 
        self.llm_with_tools = self.llm.bind_tools(self.tools)

        # 4.Create Agents
        self.researcher = ResearcherAgent(self.llm_with_tools)
        self.fact_checker = FactCheckerAgent(self.llm_with_tools)
        self.summarizer = SummarizerAgent(self.llm)

        # 5.Create tool node 
        self.tool_node = ToolNode(self.tools)

        # 6.Build Graph
        self.graph = self._build_graph()
        
        logger.info("Multi-Agent System Initialized Successfully")

    def _build_graph(self)->StateGraph:
        """
        Build the LangGraph workflow
        
        Returns:
            Compiled workflow graph
        """
        logger.info("Building Workflow Graph")

        # Researcher edges
        workflow = StateGraph(MultiAgentState)
        
        # Add nodes
        workflow.add_node("researcher", self.researcher.run)
        workflow.add_node("fact_checker", self.fact_checker.run)
        workflow.add_node("summarizer", self.summarizer.run)
        workflow.add_node("tools", self.tool_node)
        workflow.add_node("save_research", save_research_data)
        workflow.add_node("save_facts", save_verified_facts)
        
        # Set entry
        workflow.set_entry_point("researcher")
        
        # Researcher edges
        workflow.add_conditional_edges(
            "researcher",
            should_continue_research,
            {
                "tools": "tools",
                "researcher": "researcher",
                "fact_checker": "save_research"
            }
        )
        
        workflow.add_edge("save_research", "fact_checker")
        
        # Fact-checker edges
        workflow.add_conditional_edges(
            "fact_checker",
            should_continue_fact_checking,
            {
                "tools": "tools",
                "summarizer": "save_facts"
            }
        )
        
        workflow.add_edge("save_facts", "summarizer")
        workflow.add_edge("summarizer", END)
        
        # Tools edges
        workflow.add_conditional_edges(
            "tools",
            after_tools,
            {
                "researcher": "researcher",
                "fact_checker": "fact_checker"
            }
        )
        
        return workflow.compile()
    
    def research(self, query: str, max_iterations: int = 2) -> dict:
        """
        Execute research workflow
        
        Args:
            query: Research question
            max_iterations: Max research iterations
            
        Returns:
            Research results dictionary
        """
        logger.info(f"Starting research: {query}")
        
        initial_state = {
            "messages": [],
            "query": query,
            "research_data": "",
            "verified_facts": "",
            "final_report": "",
            "iteration": 0,
            "max_iterations": max_iterations
        }
        
        result = self.graph.invoke(initial_state)
        
        logger.info("Research completed successfully")
        
        return {
            "query": query,
            "research_data": result.get("research_data", ""),
            "verified_facts": result.get("verified_facts", ""),
            "final_report": result.get("final_report", ""),
            "iterations": result.get("iteration", 0),
            "success": True
        }

