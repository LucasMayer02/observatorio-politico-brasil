def self_check_node(state):
    return {
        "self_check_passed": False,
        "retry_count": state.get("retry_count", 0)
    }