"""
Agents Module - Defines all agent classes
Purpose: Separate agent logic for modularity and testing
"""

from langchain_core.messages import HumanMessage,SystemMessage
from app.agent.state import MultiAgentState
from typing import Dict 
import logging 

logger = logging.getLogger(__name__)

class ResearcherAgent():
    """
    Researcher Agent - Gathers information using tools
    
    Responsibilities:
    - Search web for current information
    - Use multiple tools to gather data
    - Provide comprehensive research findings
    """
    def __init__(self,llm_with_tools):
        self.llm = llm_with_tools
        self.name = "Researcher"

    def run(self,state:MultiAgentState)->Dict:
        """
        Execute research workflow
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with research results
        """
        query = state["query"]
        iteration = state["iteration",0]

        system_prompt = f"""You are a RESEARCHER agent with web search tools.

        Your Job: Find CURRENT, FACTUAL information about: {query}

        Available Tools:
        - web_search: Search internet for recent information
        - web_scrape: Read full content from URLs
        - calculate: Perform numerical calculations

        Strategy:
        1. Start with broad web search
        2. Search for specific aspects
        3. Look for recent developments (2025-2026)
        4. Cite sources clearly

        Iteration: {iteration + 1}"""

        logger.info(f"{self.name}: Starting research iteration {iteration+1}")
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Research thoroughly: {query}")
        ]

        response = self.llm.invoke(messages)

        return {
            "messages":[response],
            "iteration":iteration+1
        }
    

class FactCheckerAgent():
    """
    Fact-Checker Agent - Verifies information
    
    Responsibilities:
    - Verify claims from research
    - Cross-check with multiple sources
    - Rate confidence levels
    """
    def __init__(self,llm_with_tools):
        self.llm = llm_with_tools
        self.name = "Fact-Checker"
    def run(self,state:MultiAgentState)->Dict:
        """
        Execute fact-checking workflow
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with verified facts
        """
        research_data = state["research_data",""]
        system_prompt = """You are a FACT-CHECKER agent with verification tools.

        Your Job: Verify claims and assess reliability.

        Tools Available:
        - web_search: Cross-check facts
        - calculate: Verify numerical claims

        Process:
        1. Review all claims
        2. Use tools to verify questionable claims
        3. Rate confidence (High/Medium/Low)
        4. Flag unverified claims

        Output Format:
        ✅ VERIFIED: [fact] - Source: [source] (Confidence: High)
        ⚠️ NEEDS VERIFICATION: [claim] - Reason: [reason]
        🚫 REFUTED: [false claim] - Reason: [why]"""

        logger.info(f"{self.name}: Verifying Facts")

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Verify: \n\n{research_data}")
        ]
        response = self.llm.invoke(messages)

        return {
            "messages":[response],
        }
    
class SummarizerAgent():
    """
    Summarizer Agent - Creates final report
    
    Responsibilities:
    - Combine research and verified facts
    - Create structured report
    - Format in markdown
    """
    def __init__(self,llm):
        self.llm = llm
        self.name = "Summarizer"

    def run(self,state:MultiAgentState)->Dict:
        """
        Execute summarization workflow
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with final report
        """
        query = state["query"]
        research = state["research_data",""]
        verified = state["verified_facts",""]

        system_prompt = """You are a SUMMARIZER agent.

Your Job: Create a professional research report.

Structure:
# Research Report: [Topic]

## 🎯 Executive Summary
[2-3 sentences]

## 🔍 Key Findings
[Main points with sources]

## 📊 Detailed Analysis
[Comprehensive explanation]

## 💡 Insights
[Implications and outlook]

## 📚 Sources
[All sources used]"""

        logger.info(f"{self.name}: Creating final report")
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"""Report for: {query}

            Research:
            {research}

            Verified:
            {verified}"""
            )]
                
        response = self.llm.invoke(messages)
        return {
            "messages":[response],
            "final_report":response.content
        }
