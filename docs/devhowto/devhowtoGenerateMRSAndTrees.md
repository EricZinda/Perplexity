
Now let's take our knowledge of MRS and well-formed trees, and write the code that will convert a human phrase into all of the interpretations -- i.e. all of the MRS documents and all of their well-formed trees.

First, we'll write code to use the [ACE parser](http://sweaglesw.org/linguistics/ace/) to convert a phrase into an MRS document. We can use the `ACEParser` class from [`pydelphin`](https://github.com/delph-in/pydelphin) to do this. The only trick is that we need to supply a grammar file. The grammar file tells ACE which language we are speaking. The grammar file is platform dependent, so we've got a helper function that determines which one to return for the current user:
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
Next, we need to take those MRS documents and turn them into well-formed trees. For this, we'll call the function we wrote in the section on [well-formed trees](devhowtoWellFormedTree) called `valid_hole_assignments()` that does the assignments of predication labels to "holes" as discussed in that section.
~~~
    def trees_from_mrs(self, mrs):
        # Create a dict of predications using labels as the key for easy access when building trees
        mrs_predication_dict = {}
        for predication in mrs.predications:
            if predication.label not in mrs_predication_dict.keys():
                mrs_predication_dict[predication.label] = []
            mrs_predication_dict[predication.label].append(predication)

        # Iteratively return well-formed trees from the MRS
        for holes_assignments in valid_hole_assignments(mrs, self.max_holes):
            if holes_assignments is not None:
                # Now we have the assignments of labels to holes, but we need
                # to actually build the *tree* using that information
                well_formed_tree = tree_from_assignments(mrs.top, holes_assignments, mrs_predication_dict, mrs)
                yield well_formed_tree
~~~
The `tree_from_assignments()` function is not as straightforward as it might seem because our evaluation model evaluates predications in a depth first matter. Terms that are in a conjunction need to be evaluate in a particular order so that event arguments are filled in before they are used. There is a lot of detail here that really isn't important to understanding how the system works. You can browse the code for it [here](https://github.com/EricZinda/Perplexity/blob/main/perplexity/tree.py)

Finally, we can run the code that takes a phrase and generates all the trees from it:
~~~
def Example17():
    for mrs in mrss_from_phrase("every book is in a cave"):
        for tree in trees_from_mrs(mrs):
            print(tree)


# Example17() prints:
[['_a_q', 'x9', [['_cave_n_1', 'x9']], [['_every_q', 'x3', [['_book_n_of', 'x3', 'i8']], [['_in_p_loc', 'e2', 'x3', 'x9']]]]]]
[['_every_q', 'x3', [['_book_n_of', 'x3', 'i8']], [['_a_q', 'x9', [['_cave_n_1', 'x9']], [['_in_p_loc', 'e2', 'x3', 'x9']]]]]]
[['_a_q', 'x10', [['_cave_n_1', 'x10']], [['_every_q', 'x3', [['_book_n_of', 'x3', 'i8']], [['_in_p_state', 'e9', 'e2', 'x10'], ['ellipsis_ref', 'e2', 'x3']]]]]]
[['_every_q', 'x3', [['_book_n_of', 'x3', 'i8']], [['_a_q', 'x10', [['_cave_n_1', 'x10']], [['_in_p_state', 'e9', 'e2', 'x10'], ['ellipsis_ref', 'e2', 'x3']]]]]]
~~~
The [next topic](devhowtoWhichParseAndTree) will describe a heuristic for determining which of those trees is the one the user meant.
