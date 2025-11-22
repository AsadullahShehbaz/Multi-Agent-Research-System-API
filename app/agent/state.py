"""
State Module - Defines the shared state structure
Purpose: Central state definition for type safety and clarity
"""

from typing import TypedDict,List,Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages 

class MultiAgentState(TypedDict):
    """
    Shared state between all agents in the workflow
    
    Attributes:
        messages: All conversation messages (including tool calls)
        query: Original research 
        research_data: Raw data collected by researcher
        verified_facts: Facts verified by fact-checker
        final_report: Final report from summarizer
        iteration: Current iteration count
        max_iterations: Maximum allowed iterations
    """

    messages : Annotated[List[BaseMessage],add_messages]
    query : str
    research_data : str
    verified_facts : str
    final_report : str
    iteration : int
    max_iterations : int 

    
