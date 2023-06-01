from perplexity.sstring import s
from perplexity.tree import predication_from_index, find_predication_from_introduced, find_predication
from perplexity.utilities import parse_predication_name, sentence_force


# Implements the response for a given tree
# yields: response, solution_group that generated the response
# In scenarios where there is an open solution group (meaning like "files are ..." where there is an initial solution that will
# grow), this will yield once for every additional solution
def respond_to_mrs_tree(message_function, tree, solution_groups, error):
    # Tree can be None if we didn't have one of the
    # words in the vocabulary
    if tree is None:
        message = message_function(None, error)
        yield message, None
        return

    sentence_force_type = sentence_force(tree["Variables"])
    if sentence_force_type == "prop" or sentence_force_type == "prop-or-ques":
        # This was a proposition, so the user only expects
        # a confirmation or denial of what they said.
        # The phrase was "true" if there was at least one answer
        if solution_groups is not None:
            yield None, next(solution_groups)
            return

        else:
            message = message_function(tree, error)
            yield message, None
            return

    elif sentence_force_type == "ques":
        # See if this is a "WH" type question
        wh_predication = find_predication(tree["Tree"], "_which_q")
        if wh_predication is None:
            wh_predication = find_predication(tree["Tree"], "which_q")

        if wh_predication is None:
            # This was a simple question, so the user only expects
            # a yes or no.
            # The phrase was "true" if there was at least one answer
            if solution_groups is not None:
                yield "Yes.", next(solution_groups)
                return

            else:
                message = message_function(tree, error)
                yield message, None
                return

        else:
            # This was a "WH" question. Return the values of the variable
            # asked about from the solution
            # The phrase was "true" if there was at least one answer
            if solution_groups is not None:
                # Build an error term that we can use to call generate_message
                # to get the response
                index_predication = find_predication_from_introduced(tree["Tree"], tree["Index"])
                wh_variable = wh_predication.introduced_variable()

                # Get unique items from all solutions
                answer_items = set()
                solution_group = next(solution_groups)
                response = ""
                for solution in solution_group:
                    binding = solution.get_binding(wh_variable)
                    if binding.variable.combinatoric:
                        value_set = ((value, ) for value in binding.value)
                        if value_set not in answer_items:
                            answer_items.add(value_set)
                            yield message_function(tree, [-1, ["answerWithList", index_predication, value_set]]), [solution]

                    else:
                        if binding.value not in answer_items:
                            answer_items.add(binding.value)
                            yield message_function(tree, [-1, ["answerWithList", index_predication, [binding.value]]]), [solution]

            else:
                message = message_function(tree, error)
                yield message, None
                return

    elif sentence_force_type == "comm":
        # This was a command so, if it works, just say so
        # We'll get better errors and messages in upcoming sections
        if solution_groups is not None:
            yield None, next(solution_groups)

        else:
            message = message_function(tree, error)
            yield message, None


def generate_message(tree_info, error_term):
    error_predicate_index = error_term[0]
    error_arguments = error_term[1]
    error_constant = error_arguments[0] if error_arguments is not None else "no error set"
    arg_length = len(error_arguments)
    arg1 = error_arguments[1] if arg_length > 1 else None
    arg2 = error_arguments[2] if arg_length > 2 else None
    arg3 = error_arguments[3] if arg_length > 3 else None

    if error_constant == "answerWithList":
        answer_items = list(error_arguments[2])

        if len(answer_items) > 0:
            message = "\n".join([str(answer_item) for answer_item in answer_items])
            return message
        else:
            return ""

    elif error_constant == "beMoreSpecific":
        return f"Could you be more specific?"

    elif error_constant == "doesntExist":
        return s("There isn't {a arg1:sg} in the system", tree_info)

    # Used when you want to embed the error message directly in the code
    elif error_constant == "errorText":
        return error_arguments[1]

    elif error_constant == "formNotUnderstood":
        predication = predication_from_index(tree_info, error_predicate_index)
        parsed_predicate = parse_predication_name(predication.name)

        if error_arguments[1] == "notHandled":
            # The event had something that the predication didn't know how to handle
            # See if there is information about where it came from
            if "Originator" in error_arguments[2][1]:
                originator_index = error_arguments[2][1]["Originator"]
                originator_predication = predication_from_index(tree_info, originator_index)
                parsed_originator = parse_predication_name(originator_predication.name)
                return f"I don't understand the way you are using '{parsed_originator['Lemma']}' with '{parsed_predicate['Lemma']}'"

        return f"I don't understand the way you are using: {parsed_predicate['Lemma']}"

    elif error_constant == "lessThan":
        return s("There are less than {*arg2} {bare arg1:sg@error_predicate_index}", tree_info)

    elif error_constant == "moreThan":
        return s("There {'is':<arg1} more than {arg1:@error_predicate_index}", tree_info)

    elif error_constant == "moreThan1":
        return s("There is more than one {bare arg1}", tree_info)

    elif error_constant == "moreThanN":
        # TODO: Make arg1 match arg2's plural
        return s("There {'is':<*arg2} more than {*arg2} {bare arg1:@error_predicate_index}", tree_info)  # s(None, arg1, count=int(arg2))}")

    elif error_constant == "notTrueForAll":
        return s("That isn't true for all {arg1:@error_predicate_index}", tree_info)

    elif error_constant == "xIsNotY":
        return s("{arg1:@error_predicate_index} is not {arg2:@error_predicate_index}", tree_info)

    elif error_constant == "xIsNotYValue":
        return s("{arg1} is not {*arg2}", tree_info)

    elif error_constant == "valueIsNotX":
        return s("{*arg1} is not {arg2}", tree_info)

    elif error_constant == "valueIsNotValue":
        return f"{arg1} is not {arg2}"

    elif error_constant == "unexpected":
        return "I'm not sure what that means."

    elif error_constant == "unknownWords":
        lemmas_unknown = []
        lemmas_form_known = []
        for unknown_predication in error_arguments[1]:
            parsed_predicate = parse_predication_name(unknown_predication[0])
            if unknown_predication[3]:
                lemmas_form_known.append(parsed_predicate["Lemma"])
            else:
                lemmas_unknown.append(parsed_predicate["Lemma"])

        answers = []
        if len(lemmas_unknown) > 0:
            answers.append(f"I don't know the words: {', '.join(lemmas_unknown)}")

        if len(lemmas_form_known) > 0:
            answers.append(f"I don't know the way you used: {', '.join(lemmas_form_known)}")

        return " and ".join(answers)

    else:
        return None
