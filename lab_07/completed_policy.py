
"""Lab 06 — Student baseline FSM policy.

All transitions are part of the proposed course model.
Return a state name or None (hold).
"""

def transition(current_state: str, event: str) -> str | None:

    # Safety and recovery events.
    if event == "fault":
        return "normal"

    if event == "near":
        return "afraid"

    if event == "clear":
        return "normal"

    # Afraid guard: ignore lower-priority events.
    if current_state == "afraid":
        return None

    # Positive interactions.
    if event == "touch":
        return "happy"

    if event in ("button", "approach"):
        return "interested"

    # Active-state timeout.
    if event == "timeout":
        if current_state in ("interested", "happy"):
            return "normal"

    # Inactivity.
    if event == "idle" and current_state == "normal":
        return "sleepy"

    # Other combinations: hold.
    return None
