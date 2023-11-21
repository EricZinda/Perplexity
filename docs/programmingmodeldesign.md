Design this more like how you think about the scenario you are trying to achieve.

The basic model is that a predication only gets called if the phrase properties match the ones listed in properties=
Properties that aren't listed in properties= mean "requires none", i.e. if that property exists in any form it won't match

Examples are given to generate what the requirements *must be* to make those phrases work. As long as one of the parses from a given example match the properties, it will compile.  If none do, it will fail. 

If a given example generates more than one parse (often the case), the different parses might have different property requirements.  The parses the developer does not care about should be ignored and not cause a compile error. A dictionary is used in this case to indicate which properties to ignore (see below example of "Check, please")

To avoid duplication of examples and properties, users can set properties_from=function_name to use the properties defined on that function name
Often used for a group predication


@Predication(vocabulary,
             names=["_have_v_1"],
             examples=["Do you have a table?",          # --> implied table request
                       {"Example": "Check, please", "IgnoreProperties": [{'SF': 'prop-or-ques', 'TENSE': 'tensed', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}]},
                       "Do you have this table?",       # --> fact checking question
                       "What do you have?",             # --> implied menu request
                       "Do you have a|the menu|bill?",  # --> implied menu request
                       "What specials do you have?",    # --> implied request for description of specials
                       "Do I|we have the table?",       # --> ask about the state of the world
                       "Do you have a|the steak?",      # --> just asking about the steak, no implied request
                       "Do you have a bill?",           # --> implied request, kind of
                       "Do you have menus?",            # --> Could mean "do you have conceptual menus?" or "implied menu request and thus instance check"
                       "Do you have steaks?",           # --> Could mean "do you have more than one preparation of steak" or "Do you have more than one instance of a steak"
                       "We have 2 menus"                # --> fact checking question
                       ],
             properties={'SF': ['ques', 'prop'], 'TENSE': 'pres', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'})
def _have_v_1_present(context, state, e_introduced_binding, x_actor_binding, x_object_binding):