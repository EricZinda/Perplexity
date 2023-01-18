# Custom Responses to Queries
So far, we respond to any "Wh"-type query (where, what, who, etc.) by just printing out the variable assignments in the solution, like this:

~~~
? which file is small?
File(name=/documents/file1.txt, size=1000)

? where am i?
Folder(name=/, size=0)
Folder(name=/Desktop, size=0)
~~~

It is time to allow some customization to provide better answers.  For both scenarios, just giving the name of the file or folder would be clearer. For "Where am I?", we should also answer with the most specific folder since, like "in /Desktop", exhaustively listing all the folders probably isn't what the user wants.  

We can accomplish both by using the `generate_message()` function for answers to "Wh" questions just like we do for error messages. This means changing `respond_to_mrs_tree()` to create a special "error term" when we are responding with a list of answers to a query: 

~~~
def respond_to_mrs_tree(tree, solutions, error):
    
    ...
    
    elif sentence_force_type == "ques":
        
        ...
        
            # This was a "WH" question. Return the values of the variable 
            # asked about from the solution
            # The phrase was "true" if there was at least one answer
            if len(solutions) > 0:
                # Build an error term that we can use to call generate_message
                # to get the response
                index_predication = find_predicate_from_introduced(tree["Tree"], tree["Index"])
                wh_variable = wh_predication[1]
                answer_items = []
                for solution in solutions:
                    answer_items.append(solution.get_variable(wh_variable))

                message = generate_message(tree, [-1, ["answerWithList", index_predication, answer_items]])
                return message
            
            else:
                message = generate_message(tree, error)
                return message
                
~~~

The error term is in the form: `[-1, ["answerWithList", index_predication, answer_items]]`. `answerWithList` means this is a "Wh" question answer. We also pass the `index_predication` because, as described in the topic on [sentence force](../devhowto/devhowtoSentenceForce/), this indicates the predication that the sentence is *about* (aka the "syntactic head"). Having this allows us to provide different answers for different "verbs". In this case, `loc_nonsp` is acting as a verb (this behavior is also described in [that section](../devhowto/devhowtoSentenceForce/)) and so we can modify `generate_message()` to respond differently:

~~~
def generate_message(tree_info, error_term):
    
    ...
    
    elif error_constant == "answerWithList":
        answer_predication = error_arguments[1]
        answer_items = error_arguments[2]

        if len(answer_items) > 0:
            message = ""

            if answer_predication[0] == "loc_nonsp":
                # if "loc_nonsp" is the "verb", it means the phrase was
                # "Where is YYY?", so only return the "best" answer, which 
                # is the most specific one
                best_answer = ""
                for answer_item in answer_items:
                    current_answer = str(answer_item.name)
                    if len(current_answer) > len(best_answer):
                        best_answer = current_answer
                message = f"in {best_answer}"

            else:
                for answer_item in answer_items:
                    message += str(answer_item) + "\n"

            return message
        else:
            return ""
                
            ...
~~~

`generate_message()` uses the same approach as before (just printing out a list of answers) by default, but now we've added special case code when responding to `loc_nonsp`:

~~~
? where am i
in /Desktop

? which file is small
File(name=/documents/file1.txt, size=1000)
~~~