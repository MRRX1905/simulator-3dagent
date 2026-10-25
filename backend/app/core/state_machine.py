from typing import Set

class AgentState:
    IDLE = "IDLE"
    PLANNING = "PLANNING"
    EXECUTING = "EXECUTING"
    WAITING_TOOL = "WAITING_TOOL"
    OBSERVING = "OBSERVING"
    REVIEWING = "REVIEWING"
    LEARNING = "LEARNING"
    DONE = "DONE"

VALID_STATES: Set[str] = {
    AgentState.IDLE,
    AgentState.PLANNING,
    AgentState.EXECUTING,
    AgentState.WAITING_TOOL,
    AgentState.OBSERVING,
    AgentState.REVIEWING,
    AgentState.LEARNING,
    AgentState.DONE,
}

TRANSITIONS = {
    AgentState.IDLE: {AgentState.PLANNING, AgentState.LEARNING, AgentState.REVIEWING},
    AgentState.PLANNING: {AgentState.EXECUTING, AgentState.IDLE},
    AgentState.EXECUTING: {AgentState.WAITING_TOOL, AgentState.OBSERVING, AgentState.REVIEWING, AgentState.DONE},
    AgentState.WAITING_TOOL: {AgentState.EXECUTING, AgentState.OBSERVING},
    AgentState.OBSERVING: {AgentState.EXECUTING, AgentState.REVIEWING, AgentState.DONE},
    AgentState.REVIEWING: {AgentState.EXECUTING, AgentState.DONE, AgentState.IDLE},
    AgentState.LEARNING: {AgentState.EXECUTING, AgentState.IDLE},
    AgentState.DONE: {AgentState.IDLE},
}

def can_transition(current_state: str, new_state: str) -> bool:
    if new_state not in VALID_STATES:
        return False
    if current_state == new_state:
        return True
    return new_state in TRANSITIONS.get(current_state, set())
