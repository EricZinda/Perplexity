from perplexity.tree import find_predications_using_variable_ARG1
from perplexity.utilities import at_least_one_generator, system_added_arg_count, system_added_state_arg, \
    system_added_context_arg


# Return a virtual argument for a predication from a scopal argument
# This will be a generator since there could be more than one found
def scopal_argument(scopal_index, event_for_arg_index, event_value_pattern):
    # Return the actual argument created from the args passed to the predication
    # at runtime and the information originally passed in
    def scopal_argument_generator(args):
        state = args[system_added_state_arg]
        context = args[system_added_context_arg]

        def possibly_empty_generator():
            # Get the arguments we'll need from the runtime arguments
            x_what_binding = args[event_for_arg_index + system_added_arg_count]
            h_scopal_arg = args[scopal_index + system_added_arg_count]

            # Determine which events in the scopal argument we need
            scopal_events = scopal_events_modifying_individual(x_what_binding.variable.name, h_scopal_arg)
            if len(scopal_events) > 0:
                # Normalize the tree, which could return multiple solutions like any call()
                for solution in context.call(state, h_scopal_arg, normalize=True):
                    # Get the value for each event and see if it holds
                    # the pattern being searched for
                    for scopal_event in scopal_events:
                        found_binding = solution.get_binding(scopal_event)
                        if found_binding.value is not None:
                            found_value = event_value_from_pattern(found_binding.value, event_value_pattern)
                            if found_value is not None:
                                yield found_value

        # Make sure there is at least one value found
        # Otherwise this predication won't be able to execute
        # so an error should be reported
        generator = at_least_one_generator(possibly_empty_generator())
        if generator is None:
            context.report_error(["formNotUnderstood", "missing",  next(iter(event_value_pattern))])

        else:
            return generator

    return scopal_argument_generator


# Use the pattern in pattern_dict to find a value in event_dict
# The pattern is a nested set of dicts, where the last value is an
# expected type (which could be object if any value is OK):
#
# pattern example: {"LocativePreposition": {"EndLocation": VariableBinding}}
def event_value_from_pattern(event_dict, pattern_dict):
    # Get the first key from pattern_dict
    key = next(iter(pattern_dict))

    if key in event_dict:
        next_event_level = event_dict[key]
        next_pattern_level = pattern_dict[key]
        if isinstance(next_pattern_level, dict):
            return event_value_from_pattern(next_event_level, next_pattern_level)
        elif isinstance(next_event_level, next_pattern_level):
            return next_event_level

    return None


# Determine which events modify this individual
def scopal_events_modifying_individual(x_individual, h_scopal):
    events = []
    for predication in find_predications_using_variable_ARG1(h_scopal, x_individual):
        if predication.arg_types[0] == "e":
            events.append(predication.args[0])

    return events

