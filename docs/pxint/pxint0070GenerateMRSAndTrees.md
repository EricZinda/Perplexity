## Converting Phrases to MRS and Well-Formed Trees
To use our completed backtracking solver, we need to write the code that will convert a human phrase into `TreePredications` and call this solver with them. So, we need to generate all the MRS documents for the phrase and all the well-formed trees for the MRS documents.

To do this, we'll write code to use the [ACE parser](http://sweaglesw.org/linguistics/ace/) to convert a phrase into an MRS document. We can use the `ACEParser` class from [`pydelphin`](https://github.com/delph-in/pydelphin) to do this. The only trick is that we need to supply a grammar file. The grammar file tells ACE which language we are speaking. It is platform dependent, so we've got a helper function that determines which one to return for the current user:
~~~
    def mrss_from_phrase(self, phrase):
        # Don't print errors to the screen
        f = open(os.devnull, 'w')

        # Create an instance of the ACE parser and ask to give <= 25 MRS documents
        with ace.ACEParser(self.erg_file(), cmdargs=['-n', '25'], stderr=f) as parser:
            ace_response = parser.interact(phrase)

        for parse_result in ace_response.results():
            # Keep track of the original phrase on the object
            mrs = parse_result.mrs()
            mrs.surface = phrase
            yield mrs


    def erg_file(self):
        if sys.platform == "linux":
            ergFile = "erg-2020-ubuntu-perplexity.dat"

        elif sys.platform == "darwin":
            # Mac returns darwin for both M1 and Intel silicon, need to dig deeper
            unameResult = platform.uname()

            if "ARM" in unameResult.version:
                # M1 silicon
                ergFile = "erg-2020-osx-m1-perplexity.dat"

            else:
                # Intel silicon
                ergFile = "erg-2020-osx-perplexity.dat"

        else:
            ergFile = "erg-2020-ubuntu-perplexity.dat"

        return ergFile
~~~

Next, we need to take those MRS documents and turn them into well-formed trees. For this, we'll create a function called `trees_from_mrs()`. It will call the function we wrote in the section on [well-formed trees](devhowtoWellFormedTree) called `valid_hole_assignments()` that does the assignments of predication labels to "holes" as discussed in that section.  It will then call the `tree_from_assignments()` function (also included below) that does the work of actually *building a tree* from those assignments and represents the tree using the text format we designed in the [MRS to Python topic](devhowtoMRSToPython):

~~~
def trees_from_mrs(self, mrs):
    # Create a dict of predications using their labels as each key
    # for easy access when building trees
    # Note that a single label could represent multiple predications
    # in conjunction so we need a list for each label
    mrs_predication_dict = {}
    for predication in mrs.predications:
        if predication.label not in mrs_predication_dict.keys():
            mrs_predication_dict[predication.label] = []
        mrs_predication_dict[predication.label].append(predication)

    # Iteratively return well-formed trees from the MRS
    for holes_assignments in valid_hole_assignments(mrs, self.max_holes):
        # valid_hole_assignments can return None if the grammar returns something
        # that doesn't have the same number of holes and floaters (which is a grammar bug)
        if holes_assignments is not None:
            # Now we have the assignments of labels to holes, but we need
            # to actually build the *tree* using that information
            well_formed_tree = tree_from_assignments(mrs.top,
                                                     holes_assignments,
                                                     mrs_predication_dict,
                                                     mrs)
            pipeline_logger.debug(f"Tree: {well_formed_tree}")
            yield well_formed_tree
                

def tree_from_assignments(hole_label, assignments, predication_dict, mrs):
    # Get the list of predications that should fill in the hole
    # represented by labelName
    if hole_label in assignments.keys():
        predication_list = predication_dict[assignments[hole_label]]
    else:
        predication_list = predication_dict[hole_label]

    # predication_list is a list because multiple items might
    # have the same key and should be put in conjunction (i.e. be and'd together)
    conjunction_list = []
    for predication in predication_list:
        tree_node = [predication.predicate]

        # Recurse through this predication's arguments
        # and look for any scopal arguments to recursively convert
        for arg_name in predication.args.keys():
            original_value = predication.args[arg_name]

            # CARG arguments contain strings that are never
            # variables, they are constants
            if arg_name in ["CARG"]:
                new_value = original_value
            else:
                argType = original_value[0]
                if argType == "h":
                    new_value = tree_from_assignments(original_value, assignments, predication_dict, mrs)
                else:
                    new_value = original_value

            tree_node.append(new_value)

        conjunction_list.append(tree_node)

    # Since these are "and" they can be in any order
    # Sort them into an order which ensures event variable
    #   usage comes before introduction (i.e. ARG0)
    return sort_conjunctions(conjunction_list)
~~~

The `sort_conjunctions()` function isn't shown because it is not a small amount of code and it isn't important to understanding the material here. It is there because our evaluation model evaluates predications in a depth-first manner. Terms that are in conjunction need to be evaluated in a particular order so that event arguments are filled in before they are used, and `sort_conjunctions()` does this. You can browse the code for it [here](https://github.com/EricZinda/Perplexity/blob/main/perplexity/tree.py).

With all that, we can now write code that takes a phrase and generates all the trees from it:

~~~
Todo: update example
~~~
The [next topic](pxint0071WhichParseAndTree.md) will describe a heuristic for determining which of those trees is the one the user meant.

> Comprehensive source for the completed tutorial is available [here](https://github.com/EricZinda/Perplexity).