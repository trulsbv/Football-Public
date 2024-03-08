from classes import Event


def categorize_item(integer: int, group_boundaries: list[int]) -> int:
    """
    Takes an event and a list of times [5, 10, 15 ...] and returns
    the index that event belongs to:
    4 return index 0
    60 returns index 11
    5 returns index 0
    """
    for i, upper_bound in enumerate(group_boundaries):
        if integer <= upper_bound:
            return i


def times_x_fits_in_y(x: int, y: int) -> list:
    """
    Takes x and y and returns a list with the amount of times x fits in y
    """
    if x <= 0 or y <= 0:
        return []

    result = [i for i in range(x, y + 1) if i % x == 0]
    return result


def find_event(event_list: list, event_type: Event):
    types = []
    return_types = []
    if event_type == Event.Goal:
        types.append(Event.PlayGoal)
        types.append(Event.PenaltyGoal)
    elif event_type == Event.Booking:
        types.append(Event.RedCard)
        types.append(Event.YellowCard)
    else:
        types.append(event_type)

    for item in event_list:
        if type(item) in types:
            return_types.append(item)
    return return_types


def iterate_events(event_list: list, event_type: Event, frequency: int = 5) -> list:
    """
    Returns a list of when a chosen event has happened, places it in boxes
    of the given frequency: 5 gives 0-4, 5-9, 10-14 ...

    Input:
        * Type of event e.g. Goal, Card ...

    Output:
        * list of lists with the events
    """
    output = [0 for _ in range(len(times_x_fits_in_y(frequency, 90)))]
    for event in event_list:
        if isinstance(event, event_type):
            indx = categorize_item(event.time, times_x_fits_in_y(frequency, 90))
            output[indx] = output[indx] + 1
    return output
