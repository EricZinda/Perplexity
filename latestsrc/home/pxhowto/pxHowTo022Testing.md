{% raw %}## Testing
Now that we have implemented a predication, it is important to understand how to test it.  In a Perplexity application, it is very easy to enhance a predication to support one scenario and break others that used to work. So, to keep the system working well and avoid functionality regressions, you should always write at least simple functionality tests for phrases once they work.

Since the interface to a Perplexity system is simply textual user input, and the output is also text, the built-in Perplexity test functionality just records the output that you expect for a given phrase when it is working properly. Then, you can run the test again when you've changed something and it will tell you if the expected output has changed.

### Recording a test
You can see all the commands (even beyond testing) that Perplexity supports by typing "/help":

```
? /help

Commands start with /:

****** General ******
/help Get list of commands -> e.g. /help
/r Repeat the last phrase -> e.g. /r
/s Repeat the last system command (i.e. the /command) -> e.g. /s
/new Calls the passed function to get the new state to use -> e.g. /new examples.Example18_reset
/reset Resets to the initial state -> e.g. /reset
/save Saves the current world state to the ./data/default directory. If given a path, saves to that path instead. -> e.g. /save
/load Loads the current world state from the ./data/default directory. If given a path, loads from that path instead. -> e.g. /load
/timeout Sets timeout time for a given phrase -> e.g. /timeout or /timeout 20

****** Parsing ******
/show Shows tracing information from last command. Add 'all' to see all interpretations, 1 to see only first trees -> e.g. /show or /show all or /show all, 1
/soln Retrieves all solutions when parsing so they can be shown with /show. Add 'all' to see all solutions, anything else toggles the current setting -> e.g. /soln or /soln all
/genall Generates all parses (normally only the first 5 are generated) -> e.g. /genall 1 OR /genall True
/runall Runs all parses, doesn't stop after success -> e.g. /runall 1 OR /runall True
/runparse Only runs the identified parse index and optional tree index. Pass no arguments to turn off -> e.g. /runparse 1 OR /runparse 1, 0
/debugtree Shows tracing information about the tree. give a predication query after to only show trees that match it. Use '_' to mean 'anything' for an argument or the predication name -> e.g. /debugtree OR /debugtree which(x,h,h) OR /debugtree _(e,x,_,h)
/debugmrs Shows tracing information about the mrs -> e.g. /debugmrs
/findmrs ? -> e.g. /findmrs

****** Testing ******
/recordtest Starts recording a test. Finish with /createtest or /appendtest -> e.g. /record
/createtest Creates a test using name you specify based on the interactions recorded by /record -> e.g. /createtest Foo
/appendtest Appends the interactions recorded by /record to an existing test -> e.g. /appendtest Foo
/runtest Runs a test -> e.g. /runtest subdirectory/foo
/resolvetests Resolves all the test results stored in 'testresults.txt' -> e.g. /resolvetests
/logtests Logs test results to the file 'testresults.txt' -> e.g. /logtests true
/runfolder Runs all tests in a directory or directories. use '.' to run folders in the root -> e.g. /runfolder foldername or /runfolder a, b, c
/resume Resume running the last test (or sequence of tests in a folder) at the last reset before it was stopped -> e.g. /resume
```

Let's start by recording a test using the `/recordtest` command and by running the code we've done so far and doing this:

```
? /recordtest
Recording is now True

? a file is large
Yes, that is true.
Recorded (1 items).

? which file is large?
(File(name=/Desktop/file2.txt, size=10000000),)
Recorded (1 items).
```

You can see that the system is recording each interaction by the text `Recorded (1 items).` at the end of the interaction.  Perplexity will keep gathering all the commands until you are done. Then you can create a test like this:

```
? /createtest test1
Created test 'test1'
Recording is now off
```

This creates a test called "test1" and stops recording.  Tests are simply JSON files that are stored in `/perplexity/tests`.  If you open the file, you'll see:

```
{
    "WorldName": "SimplestFileSystemStateExample",
    "TestItems": [
        {
            "Command": "a file is large",
            "Expected": "Yes, that is true.",
            "Tree": "_a_q(x3,_file_n_of(x3,i8),_large_a_1(e2,x3))",
            "Enabled": true,
            "ID": "aa9b1bbc-1939-4065-bd80-5b8aeb922076"
        },
        {
            "Command": "which file is large?",
            "Expected": "(File(name=/Desktop/file2.txt, size=10000000),)",
            "Tree": "_which_q(x3,_file_n_of(x3,i8),_large_a_1(e2,x3))",
            "Enabled": true,
            "ID": "a75503d7-fc49-4369-9cc8-bb159afc2d29"
        }
    ]
}
```

The system is simply recording the input, output, the tree that was used, and an ID.  There is also an "Enabled" field that you can set to "false" if you want a particular test to be ignored.

To run the test:

```
? /runtest test1
**** Running test: /Users/ericzinda/Enlistments/Perplexity/perplexity/tests/test1.tst...


**** Begin Testing...

**** Writing LastTest: /Users/ericzinda/Enlistments/Perplexity/perplexity/tests/test1.tst...


Test: a file is large
Yes, that is true.

Test: which file is large?
(File(name=/Desktop/file2.txt, size=10000000),)

**** Testing Complete. Elapsed time: 1.74585
```

It all looks good because nothing changed. But let's change `file_n_of` to return a different file name:

```
def file_n_of(context, state, x_binding, i_binding):
    if x_binding.value is None:
#        yield state.set_x(x_binding.variable.name, ("file1.txt",))
        yield state.set_x(x_binding.variable.name, ("file2.txt",))
    elif len(x_binding.value) == 1 and x_binding.value[0] == "file1.txt":
        yield state
    else:
        report_error(["notAThing", x_binding.value, x_binding.variable.name])
        return False
```

... and run the test again:

```
? /runtest test1
**** Running test: /Users/ericzinda/Enlistments/Perplexity/perplexity/tests/test1.tst...


**** Begin Testing...

**** Writing LastTest: /Users/ericzinda/Enlistments/Perplexity/perplexity/tests/test1.tst...


Test: a file is large
Yes, that is true.

Test: which file is large?
(File(name=/documents/file1.txt, size=10000000),)

Expected: 
(File(name=/Desktop/file2.txt, size=10000000),)
(<enter>)ignore, (b)reak to end testing, (u)pdate test, (a) add alternative correct result, (d)isable test
```

Perplexity notices the output changed and tells you what it expected. Now you have to decide what to do about it:

- Maybe you meant to do the change. Press "u" to update the test to use this new output as the expected output
- Maybe you want to ignore it for now, press "enter"
- Sometimes a phrase might have multiple good answers, you can add this as an alternative using "a"
- If you want to disable the test push "d"
- You stop the test by pushing "b"

### Updating tests
Tests usually grow over time. To do this, you can record some more interactions and use the `/appendtest` command:

```
? /recordtest
Recording is now True

? is a file large?
Yes.
Recorded (1 items).

? /appendtest test1
Recording is now off

? /runtest test1
**** Running test: /Users/ericzinda/Enlistments/Perplexity/perplexity/tests/test1.tst...


**** Begin Testing...

**** Writing LastTest: /Users/ericzinda/Enlistments/Perplexity/perplexity/tests/test1.tst...


Test: a file is large
Yes, that is true.

Test: which file is large?
(File(name=/Desktop/file2.txt, size=10000000),)

Test: is a file large?
Yes.

**** Testing Complete. Elapsed time: 2.01737
```

`/appendtest` simply adds these new interactions to the end of the test. You can see that, when it is run, the whole sequence gets run.

### Resetting State
Often your tests will end up manipulating the state of the world and you'll want to reset it to try alternatives. You can do this with the `/reset` command. You give it the `module.function_name` of your reset function, like this:

```
? /reset hello_world.hello_world_FileSystemState.reset
State reset using hello_world_FileSystemState.reset().

Recorded (1 items).

? /appendtest test1
Recording is now off
```

(You'll need to use the module and function name that you've used to successfully run the example above.)

Since we appended the session, the reset will now happen at the end. This might be fine if we're going to add more interactions that we want to happen in a fresh world. But it is also a best practice to always start your tests with a reset so you know the world is starting in a known state.  You can simply edit the file and move that reset to the beginning.  It is just a JSON file. Here's what it looks like when finished:

```
{
    "WorldName": "SimplestFileSystemStateExample",
    "TestItems": [
        {
            "Command": "/reset hello_world.hello_world_FileSystemState.reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "455b3e38-cf6e-4ee0-9767-6197f47bd586"
        },
        {
            "Command": "a file is large",
            "Expected": "Yes, that is true.",
            "Tree": "_a_q(x3,_file_n_of(x3,i8),_large_a_1(e2,x3))",
            "Enabled": true,
            "ID": "aa9b1bbc-1939-4065-bd80-5b8aeb922076"
        },
        {
            "Command": "which file is large?",
            "Expected": "(File(name=/Desktop/file2.txt, size=10000000),)",
            "Tree": "_which_q(x3,_file_n_of(x3,i8),_large_a_1(e2,x3))",
            "Enabled": true,
            "ID": "a75503d7-fc49-4369-9cc8-bb159afc2d29"
        },
        {
            "Command": "is a file large?",
            "Expected": "Yes.",
            "Tree": "_a_q(x3,_file_n_of(x3,i8),_large_a_1(e2,x3))",
            "Enabled": true,
            "ID": "158d0487-a8c6-49ee-b01c-0a861a80d4ce"
        }
    ]
}
```

And now when we run it, you can see the reset happening at the beginning:

```
? /runtest test1
**** Running test: /Users/ericzinda/Enlistments/Perplexity/perplexity/tests/test1.tst...


**** Begin Testing...

**** Writing LastTest: /Users/ericzinda/Enlistments/Perplexity/perplexity/tests/test1.tst...


Test: /reset hello_world.hello_world_FileSystemState.reset
State reset using hello_world.hello_world_FileSystemState.reset().


Test: a file is large
Yes, that is true.

Test: which file is large?
(File(name=/Desktop/file2.txt, size=10000000),)

Test: is a file large?
Yes.

**** Testing Complete. Elapsed time: 2.12325
```

You can feel free to rearrange and edit the information in these test files, as long as you don't break the JSON format.

### Folders
"test1.tst" was created in the `/perplexity/tests` folder. You can also organize your tests using folders:

- `/createtest myfolder/test2`: creates a `/perplexity/tests/myfolder` folder and puts your test there.
- `/runtest myfolder/test2`: runs the test in that folder.
- `/appendtest myfolder/test2`: appends to it.

etc.

You can also run *all* the tests in a folder like this:

`/runfolder myfolder`

### Stopping and Resuming a Test
When a test breaks, you will often hit "b" to stop it, go fix it, and want to see if you fixed it. Sometimes you'd like to just restart where the break happened, especially if it is a long test.  You do this with the `/resume` command. If you type that command, Perplexity will resume the test *starting with the most recent `reset` command*. It does this because starting right where things broke might put the state in a different configuration. Restarting at the reset point ensures the state gets built up properly.

Due to this, it is always good to put resets into your test as you test different scenarios so you can `/resume` and get back to it more quickly and not have to start from the beginning.

Note that this also works for `/runfolder`.  You might have stopped the test 10 folders into the run, but `/resume` will start at that same place and skip the first 9 folders.

Also note that the test location is recorded on disk. So you can shut down your computer and come back and it will still resume in the right place.

### Logging Tests
Sometimes you can't sit there and watch the test run so you can continue over or update the tests that changed. You'd like to run the whole thing and then see what all the failures were when it is all done.  To do this, you run `/logtests` before running a test or a folder. Perplexity will then record all the failures in a file called `/perplexity/testresults.txt`. You could look at this file to see what happened, but a better way is to run `/resolvetests`. This will run you through the same interaction you would have had by just running interactively, but only on the failures.  If we redo the previous example where we intentionally broke a test, we'd get:

```
? /logtests
Log Test Results is now True

? /runtest test1
**** Running test: /Users/ericzinda/Enlistments/Perplexity/perplexity/tests/test1.tst...

Logging test results to: /Users/ericzinda/Enlistments/Perplexity/perplexity/testresults.txt

**** Begin Testing...

**** Writing LastTest: /Users/ericzinda/Enlistments/Perplexity/perplexity/tests/test1.tst...


Test: /reset hello_world.hello_world_FileSystemState.reset
State reset using hello_world.hello_world_FileSystemState.reset().


Test: a file is large
Yes, that is true.

Test: which file is large?
(File(name=/documents/file1.txt, size=10000000),)

Test: is a file large?
Yes.

**** Testing Complete. Elapsed time: 2.53661

? /resolvetests
Resolving test results in: /Users/ericzinda/Enlistments/Perplexity/perplexity/testresults.txt
**** Running test: /Users/ericzinda/Enlistments/Perplexity/perplexity/tests/test1.tst...

**** Test ID: a75503d7-fc49-4369-9cc8-bb159afc2d29
which file is large?
(File(name=/documents/file1.txt, size=10000000),)

Expected: 
(File(name=/Desktop/file2.txt, size=10000000),)
(<enter>)ignore, (b)reak to end testing, (u)pdate test, (a) add alternative correct result, (d)isable test
```

You can see that running the tests didn't say anything or stop when a test failed, but running `/resolvetests` allows you to figure out what the failure was and decide what to do with it.

Last update: 2024-10-17 by Eric Zinda [[edit](https://github.com/EricZinda/Perplexity/edit/main/docs/pxHowTo/pxHowTo022Testing.md)]{% endraw %}