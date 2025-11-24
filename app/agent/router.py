
"""
Router Module - Defines routing/decision logic
Purpose: Separate routing logic for clarity and testing
"""

from app.agent.state import MultiAgentState
from langchain_core.messages import AIMessage

# ===== ROUTING FUNCTIONS =====

def should_continue_research(state: MultiAgentState) -> str:
    """Decide next step after researcher"""
    iteration = state.get("iteration", 0)
    max_iterations = state.get("max_iterations", 2)
    messages = state.get("messages", [])
    last_message = messages[-1] if messages else None
    
    # Check if agent wants to use tools 
    if last_message and hasattr(last_message, "tool_calls") and last_message.tool_calls:
        print(f"🔧 Router: Researcher -> Tools (iteration {iteration}/{max_iterations})")
        return "tools"
    
    # FIXED: Check iteration limit - go to save_research
    if iteration >= max_iterations:
        print(f"✅ Router: Researcher -> Save Research ({max_iterations} iterations complete)")
        return "save_research"  # CRITICAL FIX: Was "fact_checker"
    
    # Continue researching
    print(f"🔄 Router: Researcher -> Researcher (iteration {iteration}/{max_iterations})")
    return "researcher"


def should_continue_fact_checking(state: MultiAgentState) -> str:
    """Decide next step after fact-checker"""
    messages = state.get("messages", [])
    fact_check_iteration = state.get("fact_check_iteration", 0)
    max_fact_check = state.get("max_fact_check_iterations", 1)
    last_message = messages[-1] if messages else None
    
    # CRITICAL: Check iteration limit FIRST
    if fact_check_iteration >= max_fact_check:
        print(f"✅ Router: Fact Checker -> Save Facts ({max_fact_check} iterations complete)")
        return "save_facts"
    
    # Check if agent wants to use tools 
    if last_message and hasattr(last_message, "tool_calls") and last_message.tool_calls:
        print(f"🔧 Router: Fact Checker -> Tools (iteration {fact_check_iteration}/{max_fact_check})")
        return "tools"
    
    print("📝 Router: Fact Checker -> Save Facts")
    return "save_facts"


def after_tools(state: MultiAgentState) -> str:
    """Decide where to return after tool execution"""
    iteration = state.get("iteration", 0)
    max_iterations = state.get("max_iterations", 2)
    research_data = state.get("research_data", "")
    
    # If we have research data, we're in fact-checking phase
    if research_data:
        print(f"🔍 Router: Tools -> Fact Checker (has research data)")
        return "fact_checker"
    
    # Otherwise, we're in research phase
    if iteration < max_iterations:
        print(f"🔬 Router: Tools -> Researcher (iteration {iteration}/{max_iterations})")
        return "researcher"
    else:
        print(f"💾 Router: Tools -> Save Research (research complete)")
        return "save_research"



# ===== HELPER FUNCTIONS =====

def extract_agent_output(state: MultiAgentState, agent_name: str) -> str:
    """Extract output from specific agent"""
    messages = state.get("messages", [])
    for message in reversed(messages):
        if isinstance(message, AIMessage):
            if isinstance(message.content, str) and len(message.content) > 50:
                return message.content
    return ""


def save_research_data(state: MultiAgentState) -> dict:
    """Save research output"""
    output = extract_agent_output(state, "Researcher")
    print(f"💾 Saved research data: {len(output)} chars")
    return {"research_data": output}


def save_verified_facts(state: MultiAgentState) -> dict:
    """Save verified facts output"""
    output = extract_agent_output(state, "Fact-Checker")
    print(f"💾 Saved verified facts: {len(output)} chars")
    return {"verified_facts": output}