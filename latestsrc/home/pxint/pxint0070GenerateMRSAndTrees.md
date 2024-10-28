{% raw %}## Converting Phrases to MRS and Well-Formed Trees
To complete our backtracking solver, we need to write the code that will convert a human phrase into `TreePredications` and call the solver with them. Up to this point, we have been hand-coding this. It is now time to have the *system* generate all the MRS documents for the phrase and all the well-formed trees for each MRS document.  Then we will have an end-to-end working system that starts from text like "a file is large" and responds to it.

To do this, we'll write code that uses the [ACE parser](http://sweaglesw.org/linguistics/ace/) (via the `ACEParser` class from [`pydelphin`](https://github.com/delph-in/pydelphin)) to convert a phrase into an MRS document. The only trick is that we need to supply a grammar file to tell ACE which language we are speaking. It is platform dependent, so we'll create a helper function that determines which one to return for the current platform. The function assumes the grammar files are all in the directory that the function is contained in. The names of the grammar files in the `/perplexity` folder of the Perplexity repository are used, and the function is actually imported from a file in that same directory. Here is the code for that function:

```
def erg_file(self):
    if sys.platform == "linux":
        ergFile = "erg-2024-daily-ubuntu-perplexity.dat"

    elif sys.platform == "darwin":
        # Mac returns darwin for both M1 and Intel silicon, need to dig deeper
        unameResult = platform.uname()

        if "ARM" in unameResult.version:
            # M1 silicon
            ergFile = "erg-2023-osx-m1-perplexity.dat"

        else:
            # Intel silicon
            ergFile = "erg-2024-daily-osx-perplexity.dat"

    else:
        ergFile = "erg-2024-daily-ubuntu-perplexity.dat"

    return os.path.join(os.path.dirname(os.path.realpath(__file__)), ergFile)
```

Using that function, we can now call ACE to get the MRS documents for a phrase:

```
def mrss_from_phrase(phrase):
    # Don't print errors to the screen
    f = open(os.devnull, 'w')

    # Create an instance of the ACE parser and ask to give <= 25 MRS documents
    with ace.ACEParser(erg_file(), cmdargs=['-n', '25'], stderr=f) as parser:
        ace_response = parser.interact(phrase)

    for parse_result in ace_response.results():
        yield parse_result.mrs()
```

... and run this sample:

```
def Example5():
    for mrs in mrss_from_phrase("2 files are large"):
        print(mrs)

# Running Example5() results in:
<MRS object (udef_q card _file_n_of _large_a_1) at 140517206087936>
<MRS object (udef_q compound number_q card _file_n_of _large_a_1) at 140517208584080>
<MRS object (loc_nonsp number_q card udef_q _file_n_of _large_a_1) at 140517206087936>
<MRS object (appos generic_entity udef_q card proper_q named _large_a_1) at 140517208584080>
<MRS object (number_q card udef_q _file_n_of _be_v_id subord _large_a_1) at 140517206087936>
<MRS object (loc_nonsp number_q card udef_q _file_n_of subord _large_a_1) at 140517208584080>
<MRS object (generic_entity udef_q card udef_q _file_n_of _be_v_id subord _large_a_1) at 140517206087936>
<MRS object (unknown generic_entity udef_q card udef_q _file_n_of _be_v_id subord _large_a_1) at 140517208584080>
<MRS object (unknown udef_q generic_entity card udef_q _file_n_of _be_v_id subord _large_a_1) at 140517206087824>
```

Thus, there were 9 parses for the phrase "2 files are large". The `delphin` Python library returns its own representation of MRS, and that's what you see printed. 

Next, we need to take the MRS documents returned from this function and turn them into well-formed trees. For this, we'll create a function called `trees_from_mrs()`. It uses the function written in the section on [well-formed trees](https://blog.inductorsoftware.com/Perplexity/home/mrscon/devhowto0020WellFormedTree) called `valid_hole_assignments()` (available [here](https://github.com/EricZinda/Perplexity/blob/main/perplexity/tree_algorithm_zinda2020.py)) that does the assignments of predication labels to "holes" as discussed in that section.  It will then call the `tree_from_assignments()` function (included below) that actually *builds* a tree from those assignments. It represents the tree using the `TreePredication` object we designed in the [Initial Solver topic](https://blog.inductorsoftware.com/Perplexity/home/pxint/pxint0040BuildSolver):

```
def trees_from_mrs(mrs):
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
    for new_mrs, holes_assignments in valid_hole_assignments(mrs, max_holes=12, required_root_label=None):
        # valid_hole_assignments can return None if the grammar returns something
        # that doesn't have the same number of holes and floaters (which is a grammar bug)
        if holes_assignments is not None:
            # Now we have the assignments of labels to holes, but we need
            # to actually build the *tree* using that information
            well_formed_tree = tree_from_assignments(mrs.top,
                                                     holes_assignments,
                                                     mrs_predication_dict,
                                                     mrs)
            yield well_formed_tree
                

def tree_from_assignments(hole_label, assignments, predication_dict, mrs, index=None):
    if index is None:
        # Use a list so the value will get modified during recursion
        index = [0]

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
        predication_name = predication.predicate

        # Recurse through this predication's arguments
        # and look for any scopal arguments to recursively convert
        args = []
        for arg_name in predication.args.keys():
            original_arg = predication.args[arg_name]

            # CARG arguments contain strings that are never
            # variables, they are constants
            if arg_name in ["CARG"]:
                final_arg = original_arg
            else:
                argType = original_arg[0]
                if argType == "h":
                    final_arg = tree_from_assignments(original_arg, assignments, predication_dict, mrs, index)
                else:
                    final_arg = original_arg

            args.append(final_arg)

        conjunction_list.append(TreePredication(index=index[0], name=predication_name, args=args))
        index[0] += 1

    return conjunction_list
```

With all that, we can now write code that takes a phrase and generates all the trees from it:

```
def Example6():
    for mrs in mrss_from_phrase("2 files are large"):
        print(mrs)
        for tree in trees_from_mrs(mrs):
            print(tree)
        print()
            
Running Example6 results in:
<MRS object (udef_q card _file_n_of _large_a_1) at 140212230080768>
[udef_q(x3,[card(2,e9,x3), _file_n_of(x3,i10)],[_large_a_1(e2,x3)])]

<MRS object (udef_q compound number_q card _file_n_of _large_a_1) at 140212232351632>
[number_q(x9,[card(2,x9,i15)],[udef_q(x3,[compound(e8,x3,x9), _file_n_of(x3,i16)],[_large_a_1(e2,x3)])])]
[udef_q(x3,[number_q(x9,[card(2,x9,i15)],[compound(e8,x3,x9), _file_n_of(x3,i16)])],[_large_a_1(e2,x3)])]

<MRS object (loc_nonsp number_q card udef_q _file_n_of _large_a_1) at 140212230080768>
[udef_q(x3,[_file_n_of(x3,i16)],[number_q(x5,[card(2,x5,i11)],[loc_nonsp(e4,e2,x5), _large_a_1(e2,x3)])])]
[number_q(x5,[card(2,x5,i11)],[udef_q(x3,[_file_n_of(x3,i16)],[loc_nonsp(e4,e2,x5), _large_a_1(e2,x3)])])]

<MRS object (appos generic_entity udef_q card proper_q named _large_a_1) at 140212232351632>
[proper_q(x5,[named(Files,x5)],[udef_q(x3,[generic_entity(x3), card(2,e11,x3)],[appos(e4,x3,x5), _large_a_1(e2,x3)])])]
[udef_q(x3,[generic_entity(x3), card(2,e11,x3)],[proper_q(x5,[named(Files,x5)],[appos(e4,x3,x5), _large_a_1(e2,x3)])])]

<MRS object (number_q card udef_q _file_n_of _be_v_id subord _large_a_1) at 140212230080768>
[subord(e17,[udef_q(x3,[_file_n_of(x3,i15)],[number_q(x5,[card(2,x5,i10)],[_be_v_id(e2,x3,x5)])])],[_large_a_1(e21,i22)])]
[subord(e17,[number_q(x5,[card(2,x5,i10)],[udef_q(x3,[_file_n_of(x3,i15)],[_be_v_id(e2,x3,x5)])])],[_large_a_1(e21,i22)])]
[udef_q(x3,[_file_n_of(x3,i15)],[subord(e17,[number_q(x5,[card(2,x5,i10)],[_be_v_id(e2,x3,x5)])],[_large_a_1(e21,i22)])])]
[udef_q(x3,[_file_n_of(x3,i15)],[number_q(x5,[card(2,x5,i10)],[subord(e17,[_be_v_id(e2,x3,x5)],[_large_a_1(e21,i22)])])])]
[number_q(x5,[card(2,x5,i10)],[subord(e17,[udef_q(x3,[_file_n_of(x3,i15)],[_be_v_id(e2,x3,x5)])],[_large_a_1(e21,i22)])])]
[number_q(x5,[card(2,x5,i10)],[udef_q(x3,[_file_n_of(x3,i15)],[subord(e17,[_be_v_id(e2,x3,x5)],[_large_a_1(e21,i22)])])])]

<MRS object (loc_nonsp number_q card udef_q _file_n_of subord _large_a_1) at 140212232351632>
[subord(e17,[udef_q(x3,[_file_n_of(x3,i16)],[number_q(x5,[card(2,x5,i11)],[loc_nonsp(e2,x3,x5)])])],[_large_a_1(e21,i22)])]
[subord(e17,[number_q(x5,[card(2,x5,i11)],[udef_q(x3,[_file_n_of(x3,i16)],[loc_nonsp(e2,x3,x5)])])],[_large_a_1(e21,i22)])]
[udef_q(x3,[_file_n_of(x3,i16)],[subord(e17,[number_q(x5,[card(2,x5,i11)],[loc_nonsp(e2,x3,x5)])],[_large_a_1(e21,i22)])])]
[udef_q(x3,[_file_n_of(x3,i16)],[number_q(x5,[card(2,x5,i11)],[subord(e17,[loc_nonsp(e2,x3,x5)],[_large_a_1(e21,i22)])])])]
[number_q(x5,[card(2,x5,i11)],[subord(e17,[udef_q(x3,[_file_n_of(x3,i16)],[loc_nonsp(e2,x3,x5)])],[_large_a_1(e21,i22)])])]
[number_q(x5,[card(2,x5,i11)],[udef_q(x3,[_file_n_of(x3,i16)],[subord(e17,[loc_nonsp(e2,x3,x5)],[_large_a_1(e21,i22)])])])]

<MRS object (generic_entity udef_q card udef_q _file_n_of _be_v_id subord _large_a_1) at 140212230080768>
[subord(e17,[udef_q(x3,[_file_n_of(x3,i15)],[udef_q(x5,[generic_entity(x5), card(2,e10,x5)],[_be_v_id(e2,x3,x5)])])],[_large_a_1(e21,i22)])]
[subord(e17,[udef_q(x5,[generic_entity(x5), card(2,e10,x5)],[udef_q(x3,[_file_n_of(x3,i15)],[_be_v_id(e2,x3,x5)])])],[_large_a_1(e21,i22)])]
[udef_q(x3,[_file_n_of(x3,i15)],[subord(e17,[udef_q(x5,[generic_entity(x5), card(2,e10,x5)],[_be_v_id(e2,x3,x5)])],[_large_a_1(e21,i22)])])]
[udef_q(x3,[_file_n_of(x3,i15)],[udef_q(x5,[generic_entity(x5), card(2,e10,x5)],[subord(e17,[_be_v_id(e2,x3,x5)],[_large_a_1(e21,i22)])])])]
[udef_q(x5,[generic_entity(x5), card(2,e10,x5)],[subord(e17,[udef_q(x3,[_file_n_of(x3,i15)],[_be_v_id(e2,x3,x5)])],[_large_a_1(e21,i22)])])]
[udef_q(x5,[generic_entity(x5), card(2,e10,x5)],[udef_q(x3,[_file_n_of(x3,i15)],[subord(e17,[_be_v_id(e2,x3,x5)],[_large_a_1(e21,i22)])])])]

<MRS object (unknown generic_entity udef_q card udef_q _file_n_of _be_v_id subord _large_a_1) at 140212232351632>
[udef_q(x12,[_file_n_of(x12,i16)],[udef_q(x4,[generic_entity(x4), card(2,e10,x4), subord(e19,[_be_v_id(e18,x12,x4)],[_large_a_1(e23,i24)])],[unknown(e2,x4)])])]
[udef_q(x4,[udef_q(x12,[_file_n_of(x12,i16)],[generic_entity(x4), card(2,e10,x4), subord(e19,[_be_v_id(e18,x12,x4)],[_large_a_1(e23,i24)])])],[unknown(e2,x4)])]
[udef_q(x4,[generic_entity(x4), card(2,e10,x4), subord(e19,[udef_q(x12,[_file_n_of(x12,i16)],[_be_v_id(e18,x12,x4)])],[_large_a_1(e23,i24)])],[unknown(e2,x4)])]

<MRS object (unknown udef_q generic_entity card udef_q _file_n_of _be_v_id subord _large_a_1) at 140212230080656>
[udef_q(x12,[_file_n_of(x12,i16)],[udef_q(x4,[generic_entity(x4), card(2,i10,x4), subord(e19,[_be_v_id(e18,x12,x4)],[_large_a_1(e23,i24)])],[unknown(e2,x4)])])]
[udef_q(x4,[udef_q(x12,[_file_n_of(x12,i16)],[generic_entity(x4), card(2,i10,x4), subord(e19,[_be_v_id(e18,x12,x4)],[_large_a_1(e23,i24)])])],[unknown(e2,x4)])]
[udef_q(x4,[generic_entity(x4), card(2,i10,x4), subord(e19,[udef_q(x12,[_file_n_of(x12,i16)],[_be_v_id(e18,x12,x4)])],[_large_a_1(e23,i24)])],[unknown(e2,x4)])]
```

You can see that each MRS parse can generate a variable number of fully-resolved trees. The [next topic](https://blog.inductorsoftware.com/Perplexity/home/pxint/pxint0071WhichParseAndTree) will describe a heuristic for determining which of those trees is the one the user meant.

> Comprehensive source for the completed tutorial is available [here](https://github.com/EricZinda/Perplexity/tree/main/samples/hello_world)

Last update: 2024-10-28 by Eric Zinda [[edit](https://github.com/EricZinda/Perplexity/edit/main/docs/pxint/pxint0070GenerateMRSAndTrees.md)]{% endraw %}