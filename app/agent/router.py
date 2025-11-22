
"""
Router Module - Defines routing/decision logic
Purpose: Separate routing logic for clarity and testing
"""

from agent.state import MultiAgentState
from langchain_core.messages import AIMessage
import logging

logger = logging.getLogger(__name__)

def should_continue_research(state:MultiAgentState)->str:
    """
    Decide next step after researcher
    
    Args:
        state: Current workflow state
        
    Returns:
        Next node name: "tools", "researcher", or "fact_checker"
    """
    iteration = state["iteration",0]
    max_iterations = state["max_iterations",2]
    messages = state["messages",""]

    last_message = messages[-1] if messages else None
    
    # Check if agents wants to use tools 
    if last_message and hasattr(last_message,"tool_calls") and last_message.tool_calls:
        logger.info("Router: Researcher -> Tools")
        return "tools"
    # #Check iteration limit
    if iteration>=max_iterations:
        logger.info("Router: Researcher > Fact Checker(max_iterations)")
        return "fact_checker"
    logger.info("Router: Researcher -> Researcher(continue)")
    return "researcher"


def should_continue_fact_checking(state:MultiAgentState)->str:
    """
    Decide next step after fact-checker
    
    Args:
        state: Current workflow state
        
    Returns:
        Next node name: "tools" or "summarizer"
    """
    messages = state["messages",""]
    last_message = messages[-1] if messages else None
    # Check if agents wants to use tools 
    if last_message and hasattr(last_message,"tool_calls") and last_message.tool_calls:
        logger.info("Router: Fact Checker -> Tools")
        return "tools"
    logger.info("Router: Fact Checker -> Summarizer")
    return "summarizer"

def after_tools(state:MultiAgentState)->str:
    """
    Decide where to return after tool execution
    
    Args:
        state: Current workflow state
        
    Returns:
        Next node name: "researcher" or "fact_checker"
    """
    research_data = state["research_data",""]
    if not research_data:
        logger.info("Router: Tools -> Researcher(no data)")
        return "researcher"
    else:
        logger.info("Router: Tools -> Fact Checker(data)")
        return "fact_checker"
    
def extract_agent_output(state:MultiAgentState,agent_name:str)->str:
    """
    Extract output from specific agent
    
    Args:
        state: Current workflow state
        agent_name: Name of agent to extract from
        
    Returns:
        Agent's output content
    """
    messages = state["messages",""]
    for message in reversed(messages):
        if isinstance(message , AIMessage):
            if isinstance(message.content,str) and len(message.content) > 50:
                return message.content
    return ""

def save_research_data(state:MultiAgentState)->str:
    """"Save research output """
    return {
        "research_data":extract_agent_output(state,"Researcher")
    }

def save_verified_facts(state:MultiAgentState)->str:
    """"Save verified facts output """
    return {
        "verified_facts":extract_agent_output(state,"Fact-Checker")
    }

    
    

    
