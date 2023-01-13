## Diagnostics
Now that we have a fully functional interactive system, we need to build in some diagnostics to make development easier. For any given interaction, we want to see all the MRS documents generated, the trees that go with them, and any terms that weren't understood (among other things). This will make debugging failures and implementing new predications *much* easier.  We'll also build in a simple "system command" feature. Any text that starts with "/" will be assumed to be a system command. We'll use this to implement "/show" which will show the MRS and trees for the last command.

To do this, we'll build up a JSON document to serve as the record of what happened during an interaction. You can see the basic approach below. `interaction_record` is the field on `UserInterface` that will keep the JSON record.  As the code progresses, it adds more information into the document:

~~~
class UserInterface(object):
    
    ...
    
    # response_function gets passed three arguments:
    #   response_function(mrs, solutions, error)
    # It must use them to return a string to say to the user
    # Builds up a record of what happened so diagnostics
    # can be printed later
    def interact_once(self, response_function):
        # input() pauses the program and waits for the user to
        # type input and hit enter, and then returns it
        user_input = str(input("? "))
        
        # If this was a system command, do whatever it does
        # and then wait for the next one
        if self.handle_command(user_input):
            return

        self.interaction_record = {"UserInput": user_input,
                                   "Mrss": [],
                                   "ChosenMrsIndex": None,
                                   "ChosenTree": None,
                                   "ChosenResponse": None}

        # Loop through each MRS and each tree that can be
        # generated from it...
        for mrs in self.mrss_from_phrase(user_input):
            mrs_record = {"Mrs": mrs,
                          "UnknownWords": self.unknown_words(mrs),
                          "Trees": []}
            self.interaction_record["Mrss"].append(mrs_record)
            
        ....
~~~

Then, afterward, the user can give the command `/show` and see the MRS, trees, etc. The code for `handle_command()` is a [very strightforward but kind of long](https://github.com/EricZinda/Perplexity/blob/main/perplexity/user_interface.py) so it isn't shown here. The [code to print out the tree in text form](https://github.com/EricZinda/Perplexity/blob/main/perplexity/print_tree.py) is not shown below because that's a whole different tutorial and not relevant to learning DELPH-IN.

With that in place, we can more clearly see how a phrase like "a file is deleted" gets interpreted by the system. Note that the `/show` command doesn't show a tree because none was generated and used (because a word wasn't understood).  Giving the `/show all` command allows the potential trees to be seen:

~~~
def Example16():
    ShowLogging("Pipeline")

    state = State([Actor(name="Computer", person=2),
                   Folder(name="Desktop"),
                   Folder(name="Documents"),
                   File(name="file1.txt", size=2000000)])

    user_interface = UserInterface(state, vocabulary)

    while True:
        user_interface.interact_once(respond_to_mrs_tree)
        print()
        
# Running Example16() produces:
? a file is deleted
I don't know the way you used: delete

? /show
User Input: a file is deleted
1 Parses

***** CHOSEN Parse #0:
[ "a file is deleted"
  TOP: h0
  INDEX: e2 [ e SF: prop TENSE: pres MOOD: indicative PROG: - PERF: - ]
  RELS: < [ _a_q<0:1> LBL: h4 ARG0: x3 [ x PERS: 3 NUM: sg IND: + ] RSTR: h5 BODY: h6 ]
          [ _file_n_of<2:6> LBL: h7 ARG0: x3 ARG1: i8 ]
          [ _delete_v_1<10:17> LBL: h1 ARG0: e2 ARG1: i9 ARG2: x3 ] >
  HCONS: < h0 qeq h1 h5 qeq h7 >
  ICONS: < e2 topic x3 > ]

Unknown words: [('_delete_v_1', ['e', 'i', 'x'], 'prop', True)]

? /show all
User Input: a file is deleted
1 Parses

***** CHOSEN Parse #0:
[ "a file is deleted"
  TOP: h0
  INDEX: e2 [ e SF: prop TENSE: pres MOOD: indicative PROG: - PERF: - ]
  RELS: < [ _a_q<0:1> LBL: h4 ARG0: x3 [ x PERS: 3 NUM: sg IND: + ] RSTR: h5 BODY: h6 ]
          [ _file_n_of<2:6> LBL: h7 ARG0: x3 ARG1: i8 ]
          [ _delete_v_1<10:17> LBL: h1 ARG0: e2 ARG1: i9 ARG2: x3 ] >
  HCONS: < h0 qeq h1 h5 qeq h7 >
  ICONS: < e2 topic x3 > ]

Unknown words: [('_delete_v_1', ['e', 'i', 'x'], 'prop', True)]

-- Parse #0, Tree #0: 

          ┌────── _file_n_of(x3,i8)
_a_q(x3,RSTR,BODY)
               └─ _delete_v_1(e2,i9,x3)

[['_a_q', 'x3', [['_file_n_of', 'x3', 'i8']], [['_delete_v_1', 'e2', 'i9', 'x3']]]]
Error: None
Response: None

? 
~~~
