DROPPED_MAX = 10
ESCLATED_ABOVE =200


def tag_outcome(duration_seconds):
    if duration_seconds <= DROPPED_MAX:
        return "dropped"
    elif duration_seconds > ESCLATED_ABOVE:
        return "escalated"
    else:
        return "resolved"