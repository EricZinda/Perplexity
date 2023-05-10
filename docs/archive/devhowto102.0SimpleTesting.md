## Simple Testing
It is easy to enhance a predication to support one scenario and break others. So, to keep the system working well and avoid functionality regressions, we're going to build a very simple testing system.

### Reset
First we need to add a command that goes hand-in-hand with many tests: `/reset`. `/reset` allows a test to reset the application to its initial state. It allows a single test to try various phrases, each from a fresh start. It is also great for building up a set of tests and running them one after the other: `/reset` allows the state to be in a known state at the beginning of each test.

It is implemented by modifying the `UserInterface` class to take a `reset` *function* instead of a `State` object. The `State` object is then created by calling that function. This allows the state to be recreated at any time by calling the function again:

~~~
class UserInterface(object):
    def __init__(self, reset, vocabulary, response_function):
        self.max_holes = 13
        self.reset = reset
        self.state = reset()
     
     ...
    
     
def command_reset(ui, arg):
    ui.state = ui.reset()
    return f"state reset."
    
    
command_data = {
     
    ...
          
    "reset": {"Function": command_reset, "Category": "General",
              "Description": "Resets to the initial state",
              "Example": "/reset"},
    
    ...


def Example16_reset():
    return State([Actor(name="Computer", person=2),
                  Folder(name="Desktop"),
                  Folder(name="Documents"),
                  File(name="file1.txt", size=2000000)])
                                
                                
def Example16():
    # ShowLogging("Pipeline")

    def reset():
    user_interface = UserInterface(Example16_reset, vocabulary, respond_to_mrs_tree)

    while True:
        user_interface.interact_once()
        print()
~~~

Now any test will be able to include the command `/reset` to go to a known starting point.


### New State
`/new` is another command that is handy when testing. You provide it with a "reset function" and it uses the function to load in new state. This allows a single test to test different state configurations. It uses a new `import_function_from_names()` function to convert the module and function names from strings to a usable function.
 
~~~
def command_new(ui, arg):
    arg_parts = arg.split(".")
    if len(arg_parts) != 2:
        print("reset function must be in the form: module_name.function_name")
        return True

    ui.reset = import_function_from_names(arg_parts[0], arg_parts[1])
    return command_reset(ui, arg)
    
    
# Takes a pair of module and function names as strings and
# imports the module and returns the function
def import_function_from_names(module_name, function_name):
    importlib.import_module(module_name)
    module = sys.modules[module_name]
    function = getattr(module, function_name)
    return function
    
    
command_data = {
     
    ...
          
    "new": {"Function": command_new, "Category": "General",
            "Description": "Calls the passed function to get the new state to use",
            "Example": "/new examples.Example18_reset"},
    
    ...
~~~



### Testing
We'll start by going through how to use the testing system and then describe how it is built.

Tests are created by recording them through user interaction.  For example, here's how a simple test can be created:

~~~
? /record
Recording is now True

? /reset
state reset.
Recorded (1 items).

? a file is large
Recorded (2 items).
Yes, that is true.

? /createtest docstest
Created test 'docstest'
Recording is now off
~~~

After that sequence, a test called `docstest` has been created in the system. Tests are simple recordings of interaction sessions, stored in JSON files.  The JSON file remembers the way to create the initial state: 

- `ResetModule` is the module that contains the reset function
- `ResetFunction` is the function to call to get initial state

... and has a list of test items in it. Each test item represents one user interaction. Each has:

- The `Command` the user gave
- The `Expected` result from the system
- The `Tree` that generated that result (just for debugging)
- Whether it is `Enabled` or not 
- A unique `ID`

Here's the JSON file for the test we recorded above:
~~~
{
    "ResetModule": "examples",
    "ResetFunction": "Example16_reset",
    "TestItems": [
        {
            "Command": "/reset",
            "Expected": "state reset.",
            "Tree": null,
            "Enabled": true,
            "ID": "8290fec8-aff8-48b7-94db-2f58512c0e27"
        },
        {
            "Command": "a file is large",
            "Expected": "Yes, that is true.",
            "Tree": "[['_a_q', 'x3', [['_file_n_of', 'x3', 'i8']], [['_large_a_1', 'e2', 'x3']]]]",
            "Enabled": true,
            "ID": "a49edbca-8096-4fe4-8f92-29c8f4d2dcba"
        }
    ]
}
~~~

A test can be run like this:

~~~
? /runtest docstest
State reset using examples.Example16_reset().

**** Begin Testing...


Test: /reset
state reset.

Test: a file is large
Yes, that is true.

**** Testing Complete.
~~~

You can see that the test system starts by initializing the state for the test and then plays back the recorded commands. It compares the system response to what it was when the test was recorded and, if the value is different, a prompt appears allowing you to take action. For example, if we change the `Expected` field of the JSON file directly to force a test to fail, like this:

~~~
{
     ...
     
        {
            "Command": "a file is large",
            "Expected": "No way!",
            "Tree": "[['_a_q', 'x3', [['_file_n_of', 'x3', 'i8']], [['_large_a_1', 'e2', 'x3']]]]",
            "Enabled": true,
            "ID": "21322fb0-fcce-453e-8904-6ab7a4a70a53"
        }
    ]
}
~~~

When run, you will see a prompt asking what you want to do:

~~~
? /runtest docstest
State reset using examples.Example16_reset().

**** Begin Testing...


Test: /reset
state reset.

Test: a file is large
Yes, that is true.

Expected: No way!
(<enter>)ignore, (b)reak to end testing, (u)pdate test, (d)isable test
u

**** Testing Complete.
~~~
In this case, `u` was selected and so the test JSON gets updated with the new value.

The commands are plugged in using the command system we built in the [previous topic](devhowtoDiagnostics). Using the `/help` command prints a list of what is now available:

~~~
? /help

...

/reset Resets to the initial state -> e.g. /reset

...

****** Testing ******
/record Starts recording a test. Finish with /createtest or /appendtest -> e.g. /record
/createtest Creates a test using name you specify based on the interactions recorded by /record -> e.g. /createtest Foo
/appendtest Appends the interactions recorded by /record to an existing test -> e.g. /appendtest Foo
/runtest Runs a test -> e.g. /runtest subdirectory/foo
/runfolder Runs all tests in a directory -> e.g. /runfolder foldername
~~~

### Creating the Tutorial Tests
Now we can create a test that covers all the scenarios we've done in the tutorial to make sure we don't break any of them as we continue adding code:

~~~
? /recordtest
Recording is now True

? /new examples.Example18_reset
State reset using examples.Example18_reset().
Recorded (1 items).

? a file is large
Recorded (2 items).
a file is not large

? which files are small
Recorded (3 items).
File(name=file1.txt, size=1000000)

? delete a large file
Recorded (4 items).
There isn't 'a large file' in the system

? delete a file
Recorded (5 items).
Done!

? a file is large
Recorded (6 items).
There isn't 'a file' in the system

? which files are small
Recorded (7 items).
There isn't 'a file' in the system
~~~

There really isn't anything we can do with folders yet except delete them so:

~~~
? delete a folder
Recorded (8 items).
~~~

To test "very" we need a different world state that includes a very large file:

~~~
def Example18a_reset():
    return State([Folder(name="Desktop"),
                   Folder(name="Documents"),
                   File(name="file1.txt", size=20000000),
                   File(name="file2.txt", size=1000000)])
~~~

And we can use our new `/new` command to use it in the test:

~~~
? /new examples.Example18a_reset
State reset using examples.Example18a_reset().
Recorded (9 items).

? which file is very large?
Recorded (10 items).
File(name=file1.txt, size=20000000)

? delete you
Recorded (11 items).
I can't delete you

? he deletes a file
I don't know the way you used: delete
~~~

Now we have a set of tests that we can run as we add to the system to make sure phrases that used to work still do:

~~~
? /runtest tutorial
State reset using examples.Example18_reset().

**** Begin Testing...


Test: /new examples.Example18_reset
State reset using examples.Example18_reset().

Test: a file is large
a file is not large

Test: delete a large file
There isn't 'a large file' in the system

    ...
    
~~~

### Testing Implementation
The source for the testing commands isn't included as part of the discussed tutorial since it has nothing specifically to do with DELPH-IN. However, the source is part of the project and can be found [here](https://github.com/EricZinda/Perplexity/blob/main/perplexity/test_manager.py).
