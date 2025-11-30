"""
State Module - Defines the shared state structure
Purpose: Central state definition for type safety and clarity
"""

from typing import TypedDict,List,Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages 

class MultiAgentState(TypedDict):
    """State for the multi-agent research system"""

    messages : Annotated[List[BaseMessage],add_messages]
    query : str
    research_data : str
    verified_facts : str
    final_report : str
    iteration : int
    max_iterations : int 
    fact_check_iteration : int
    fact_check_max_iterations : int

    
