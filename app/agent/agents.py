"""
Agents Module - Defines all agent classes
Purpose: Separate agent logic for modularity and testing
"""

from langchain_core.messages import HumanMessage,SystemMessage,ToolMessage
from app.agent.state import MultiAgentState
from typing import Dict 


# ===== AGENTS =====

class ResearcherAgent:
    """Researcher agent that conducts initial research"""
    
    def __init__(self, llm, tools):
        self.llm = llm
        self.llm_with_tools = llm.bind_tools(tools)
        self.name = "Researcher"
    
    def __call__(self, state: MultiAgentState):
        """Execute researcher agent"""
        iteration = state.get("iteration", 0)
        query = state.get("query", "")
        messages = state.get("messages", [])
        
        print(f"🔬 Researcher: Starting iteration {iteration + 1} for '{query}'")
        
        # Check if we have previous research
        tool_messages = [msg for msg in messages if isinstance(msg, ToolMessage)]
        has_results = len(tool_messages) > 0
        
        if not has_results:
            instruction = "Use the web_search tool NOW to find information. Make your first search."
        else:
            instruction = "Review the search results. Either search for more details OR provide a summary of findings."
        
        system_msg = SystemMessage(content=f"""You are a research assistant.

Query: "{query}"

{instruction}

Current iteration: {iteration + 1}
""")
        
        conversation = [system_msg] + messages
        response = self.llm_with_tools.invoke(conversation)
        
        print(f"✅ Researcher: Completed iteration {iteration + 1}")
        if hasattr(response, "tool_calls") and response.tool_calls:
            print(f"   📞 Making {len(response.tool_calls)} tool call(s)")
        
        return {
            "messages": [response],
            "iteration": iteration + 1
        }




class FactCheckerAgent:
    """Fact-checker agent that verifies research"""
    
    def __init__(self, llm, tools):
        self.llm = llm
        self.llm_with_tools = llm.bind_tools(tools)
        self.name = "Fact-Checker"
    
    def __call__(self, state: MultiAgentState):
        """Execute fact-checker agent"""
        research_data = state.get("research_data", "")
        query = state.get("query", "")
        fact_check_iteration = state.get("fact_check_iteration", 0)
        max_fact_check = state.get("max_fact_check_iterations", 1)
        
        print(f"🔍 Fact-Checker: Iteration {fact_check_iteration + 1}/{max_fact_check}")
        print(f"   Research data: {len(research_data)} chars")
        
        # Use research_data directly, or extract from messages if empty
        if not research_data or len(research_data) < 50:
            tool_contents = [
                msg.content for msg in state.get("messages", [])
                if isinstance(msg, ToolMessage)
            ]
            if tool_contents:
                research_data = "\n\n".join(tool_contents[-3:])  # Last 3 tool results
                print(f"   ⚠️  Using last 3 tool results: {len(research_data)} chars")
        
        # CRITICAL: Restrictive prompt to avoid excessive tool use
        system_msg = SystemMessage(content=f"""You are a fact-checking assistant.

Query: "{query}"

Research findings (excerpt):
{research_data[:2000]}...

Instructions:
1. Identify 3-5 key claims from the research
2. Assess their credibility
3. ONLY use web_search if you find a SUSPICIOUS or DOUBTFUL claim
4. DO NOT search for general verification - trust reputable sources
5. Provide a brief fact-check summary

Iteration: {fact_check_iteration + 1}/{max_fact_check}

Be efficient - avoid unnecessary searches.""")
        
        # Only use recent messages to avoid context bloat
        messages = [system_msg] + state.get("messages", [])[-8:]
        response = self.llm_with_tools.invoke(messages)
        
        print("✅ Fact-Checker: Verification complete")
        if hasattr(response, "tool_calls") and response.tool_calls:
            print(f"   📞 Making {len(response.tool_calls)} verification call(s)")
        
        return {
            "messages": [response],
            "fact_check_iteration": fact_check_iteration + 1
        }


class SummarizerAgent:
    """Summarizer agent that creates final report"""
    
    def __init__(self, llm):
        self.llm = llm
        self.name = "Summarizer"
    
    def __call__(self, state: MultiAgentState):
        """Execute summarizer agent"""
        query = state.get("query", "")
        research_data = state.get("research_data", "")
        verified_facts = state.get("verified_facts", "")
        
        print(f"📝 Summarizer: Creating final report")
        print(f"   Research: {len(research_data)} chars")
        print(f"   Verified: {len(verified_facts)} chars")
        
        system_msg = SystemMessage(content=f"""Create a comprehensive report for: "{query}"

Research Data:
{research_data}

Verified Facts:
{verified_facts}

Instructions:
1. Write an executive summary
2. Present key findings
3. Note any uncertainties
4. Make it clear and professional

Use markdown formatting.""")
        
        response = self.llm.invoke([system_msg])
        
        print("✅ Report complete!")
        
        return {
            "messages": [response],
            "final_report": response.content
        }


    

