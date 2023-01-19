## `this_q_dem` and "In Scope"
The word "this" as in "this folder" means something along the lines of "the one right here" or "the one most obviously in focus". We can cover a lot of cases by implementing a notion of "scope" that we will use to implement many predications.  One way to think about "in scope" is to think through what the user would expect when they say "this" with respect to the objects in the system:

- "this folder": Most likely means "the current folder", which is ["the one I am in"](devvocabLoc_nonspAndPlace)
- "this file": This is ambiguous since the user is never "in" a file (although we might allow that to allow searching around a file at some point!).  It *might* mean "the one file that is in the directory", in which case it would be equivalent to "*the* file"
- "this machine": Means the entire computer if we implement the notion of "machine/computer/device". As in "what large files are on this machine?"

Let's start with the first case and implement "this folder". If we just type in "this folder", the following tree is produced. Since the ERG doesn't know what to do with "this folder", it produces a predication called `unknown` which effectively means "the user didn't say something that was expected" (more information is [here](https://blog.inductorsoftware.com/docsproto/erg/ErgSemantics_Fragments/)):

~~~
                 ┌────── _folder_n_of(x4,i9)
_this_q_dem(x4,RSTR,BODY)
                      └─ unknown(e2,x4)
~~~

`_this_q_dem` is a *quantifier* because it has the type `_q_` and it has the standard quantifier arguments `RSTR` and `BODY`.  As described in the topic on [MRS](https://blog.inductorsoftware.com/docsproto/howto/devhowto/devhowtoMRS/#quantifier-predications), the job of a quantifier is to say "how much of" the `RSTR` should be applied to the `BODY`.  In the case of `_this_q_dem`, "how much of" really means "which", as in: *which* `RSTR` should be applied to the body. The variable being quantified is passed in its first argument (`x4` in the example above).

We'll start by implementing this "which" semantic by copying [the code we implemented for `a_q`](https://blog.inductorsoftware.com/docsproto/howto/devhowto/devhowtoQuantifierErrors/). But, where `a_q` just returns "a single arbitrary" item, `_this_q_dem` will only return an item that is "in scope" as determined by a new `in_scope()` function:

~~~
def in_scope(state, obj):
    # obj is in scope if it is the folder the user is in
    user = state.user()
    if user.current_directory == obj:
        return True


@Predication(vocabulary, names=["_this_q_dem"])
def this_q_dem(state, x_variable, h_rstr, h_body):
    # Run the RSTR which should fill in the variable with an item
    rstr_found = False
    for solution in call(state, h_rstr):
        if in_scope(solution, solution.get_variable(x_variable)):
            rstr_found = True

            # Now see if that solution works in the BODY
            body_found = False
            for body_solution in call(solution, h_body):
                yield body_solution
                body_found = True

            if body_found:
                # If it works, stop looking. This one is "this" item we are looking for
                break

    if not rstr_found:
        # Ignore whatever error the RSTR produced, this is a better one
        # Report the variable's English representation as it would be in the BODY
        report_error(["doesntExist", ["AtPredication", h_body, x_variable]], force=True)
~~~

Just by implementing this (so to speak), we can already do a lot in the system because it will work with other predications we've already implemented like `where_q`:

~~~
def Example21_reset():
    return FileSystemState(FileSystemMock([(True, "/documents/file1.txt", {"size": 1000}),
                                           (False, "/Desktop", {}),
                                           (True, "/Desktop/file2.txt", {"size": 10000000}),
                                           (True, "/Desktop/file3.txt", {"size": 1000})],
                                          "/Desktop"))


def Example21():
    user_interface = UserInterface(Example21_reset, vocabulary, respond_to_mrs_tree)

    while True:
        user_interface.interact_once()
        print()
        
        
? where am i
in /documents

? where is this folder
in /
~~~

... and `_large_a_1`:

~~~
? this folder is large
this folder is not large
~~~

Great! Now let's see how it works with files:

~~~
? this file is large
Yes, that is true.
~~~

This is a bug since there are two files in the state returned by `Example21_reset()`: `/Desktop/file1.txt` and `/Desktop/file2.txt`. "This" is ambiguous in this case.  We need to modify `this_q_dem` to return an error when it is ambiguous.

~~~
def this_q_dem(state, x_variable, h_rstr, h_body):
    # Run the RSTR which should fill in the variable with an item
    rstr_single_solution = None
    for solution in call(state, h_rstr):
        if in_scope(solution, solution.get_variable(x_variable)):
            if rstr_single_solution is None:
                rstr_single_solution = solution
            else:
                # Make sure there is only one since "this" shouldn't be ambiguous
                report_error(["moreThanOneInScope", ["AtPredication", h_body, x_variable]], force=True)
                return

    if rstr_single_solution is not None:
        # Now see if that solution works in the BODY
        body_found = False
        for body_solution in call(rstr_single_solution, h_body):
            yield body_solution

    else:
        # Ignore whatever error the RSTR produced, this is a better one
        # Report the variable's English representation as it would be in the BODY
        report_error(["doesntExist", ["AtPredication", h_body, x_variable]], force=True)


def generate_message(tree_info, error_term):

    ...
    
    elif error_constant == "moreThanOneInScope":
        arg1 = english_for_delphin_variable(error_predicate_index, error_arguments[1], tree_info)
        return f"There is more than one '{arg1}' where you are"
~~~

Now if we run it again:

~~~
? this file is large
There is more than one 'this file' where you are
~~~

Much better!
