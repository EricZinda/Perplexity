## `_in_p_loc`
Phrases using "in" such as, "What is in this folder?" can generate several predications representing "in", one of which is `in_p_loc(e,x,x)`:

~~~
[ "what is in this folder?"
  TOP: h0
  INDEX: e2 [ e SF: ques TENSE: pres MOOD: indicative PROG: - PERF: - ]
  RELS: < [ thing<0:4> LBL: h4 ARG0: x3 [ x PERS: 3 NUM: sg ] ]
          [ which_q<0:4> LBL: h5 ARG0: x3 RSTR: h6 BODY: h7 ]
          [ _in_p_loc<8:10> LBL: h1 ARG0: e2 ARG1: x3 ARG2: x8 [ x PERS: 3 NUM: sg IND: + ] ]
          [ _this_q_dem<11:15> LBL: h9 ARG0: x8 RSTR: h10 BODY: h11 ]
          [ _folder_n_of<16:22> LBL: h12 ARG0: x8 ARG1: i13 ] >
  HCONS: < h0 qeq h1 h6 qeq h4 h10 qeq h12 > ]

             ┌────── thing(x3)
which_q(x3,RSTR,BODY)                 ┌────── _folder_n_of(x8,i13)
                  └─ _this_q_dem(x8,RSTR,BODY)
                                           └─ _in_p_loc(e2,x3,x8)
~~~

`_in_p_loc(e2,x3,x8)` is true when the `x3` argument represents a thing which is "in" the `x8` argument. As always with the [predication contract](../devhowto/devhowtoPredicationContract), this predication can also return solutions to what the object in `x3` "is in" if `x8` is unbound, or what is "in" `x8` if `x3` is unbound.

To implement it, we will give the objects in the system two methods: `containers()` which returns all the things that an object is contained in, and `contained_items()` for all the things contained within an object:

~~~
class Folder(Container):

    ...
    
    def contained_items(self):
        for item in self.file_system.contained_items(self):
            yield item

    ...
    
    def containers(self):
        yield from self.all_locations()
        
        
class File(Container):
    
    ...

    def containers(self):
        yield from self.all_locations()
        

class FileSystemMock(FileSystem):
    
    ...
    
    def contained_items(self, folder):
        for item in self.items.items():
            if os.path.dirname(item[0]) == folder.name:
                yield item[1]

~~~

The `Folder` object delegates to the `FileSystem` object to return all the items it contains so that we can use our mock object to test the system. The `File` object doesn't have a `contained_items()` method since it doesn't (yet) have a reason to contain anything. It will eventually when we support looking for text in files.

Now we can implement the `_in_p_loc` predication:

~~~
def in_p_loc(state, e_introduced_binding, x_actor_binding, x_location_binding):
    if x_actor_binding.value is not None:
        if x_location_binding.value is not None:
            if hasattr(x_location_binding.value, "contained_items"):
                # x_actor is "in" x_location if x_location contains it
                for item in x_location_binding.value.contained_items(x_location_binding.variable):
                    if x_actor_binding.value == item:
                        # Variables are already set,
                        # no need to set them again, just return the state
                        yield state

        else:
            # Need to find all the things that x_actor is "in"
            if hasattr(x_actor_binding.value, "containers"):
                for item in x_actor_binding.value.containers(x_actor_binding.variable):
                    yield state.set_x(x_location_binding.variable.name, item)

    else:
        # Actor is unbound, this means "What is in X?" type of question
        # Whatever x_location "contains" is "in" it
        if hasattr(x_location_binding.value, "contained_items"):
            for location in x_location_binding.value.contained_items(x_location_binding.variable):
                yield state.set_x(x_actor_binding.variable.name, location)

    report_error(["thingHasNoLocation", x_actor_binding.variable.name, x_location_binding.variable.name])
    
    
def generate_message(tree_info, error_term):
    
    ...
    
    elif error_constant == "thingHasNoLocation":
        arg1 = english_for_delphin_variable(error_predicate_index, error_arguments[1], tree_info)
        arg2 = english_for_delphin_variable(error_predicate_index, error_arguments[2], tree_info)
        return f"{arg1} is not in {arg2}"
~~~

And now we can ask all kinds of things from the system:

~~~
def Example22_reset():
    return FileSystemState(FileSystemMock([(True, "/documents/file1.txt", {"size": 1000}),
                                           (False, "/Desktop", {"size": 10000000}),
                                           (True, "/Desktop/file2.txt", {"size": 10000000}),
                                           (True, "/Desktop/file3.txt", {"size": 1000})],
                                          "/Desktop"))


def Example22():
    user_interface = UserInterface(Example22_reset, vocabulary, respond_to_mrs_tree)

    while True:
        user_interface.interact_once()
        print()
        
# Running Example22 gives:

? what is in this folder?
File(name=/Desktop/file2.txt, size=10000000)
File(name=/Desktop/file3.txt, size=1000)


? what am I in?
Folder(name=/Desktop, size=10000000)
Folder(name=/, size=0)


? Is a file in this folder?
Yes.

? Is a folder in this folder?
a folder is not in this folder

? Which files are in this folder?
File(name=/Desktop/file2.txt, size=10000000)
File(name=/Desktop/file3.txt, size=1000)
~~~

> Comprehensive source for the completed tutorial is available [here](https://github.com/EricZinda/Perplexity).