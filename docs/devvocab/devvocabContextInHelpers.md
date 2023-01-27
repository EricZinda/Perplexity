## Returning Errors From Helper Functions
As described in the section on [returning robust failures](../devhowto/devhowtoRobustFailure), errors in the system are reported using the MRS variable names instead of the actual instance currently being accessed, like this:

~~~
@Predication(vocabulary, names=["_file_n_of"])
def file_n_of(state, x, i):
    x_binding = state.get_binding(x)
    if x_binding is None:
        iterator = state.all_individuals(x)
    else:
        iterator = [x_binding]

    for binding in iterator:
        if isinstance(binding.value, File):
            new_state = state.set_x(x, binding.value)
            yield new_state
        else:
            report_error(["xIsNotY", x, "file"])
~~~

One challenge with this approach is that the code reporting the error is not always in the predication function itself.  For example, the code for `in_p_loc` calls the `contained_items()` method of the location it is passed to see if the `x_actor` is "in" the `x_location`:

~~~
@Predication(vocabulary, names=["_in_p_loc"])
def in_p_loc(state, e_introduced, x_actor, x_location):
    x_actor_value = state.get_variable(x_actor)
    x_location_value = state.get_variable(x_location)

    if x_actor_value is not None:
        if x_location_value is not None:
            # x_actor is "in" x_location if x_location contains it
            for item in x_location_value.contained_items():
                if x_actor_value == item:
                    # Variables are already set,
                    # no need to set them again, just return the state
                    yield state

    ...    
    
~~~

Now that we've introduced the ability to specify names using strings, the user can say things like:

> what is in "bad directory"?

... where "bad directory" doesn't exist.  We need to represent "bad directory" as a `Directory` object (even though it doesn't exist), for the cases where the user is doing something like:

> create directory 'bad directory'

So we can't just return an error when the text "bad directory" is [being converted to objects in `fw_seq`](devvocabFileDirectoryNames). The "this thing doesn't exist" error needs to happen in the line above where we ask to iterate through the contained objects:

~~~
    ...
    
            for item in x_location_value.contained_items():
            
            ...
~~~

To do this we'll have to start passing the variable name to helper methods so that they can return proper errors, like this:

~~~
@Predication(vocabulary, names=["_in_p_loc"])
def in_p_loc(state, e_introduced, x_actor, x_location):
    x_actor_binding = state.get_binding(x_actor)
    x_location_binding = state.get_binding(x_location)

    if x_actor_binding is not None:
        if x_location_binding is not None:
            # x_actor is "in" x_location if x_location contains it
            for item in x_location_binding.value.contained_items(x_location_binding.variable):
                if x_actor_binding.value == item:
                    # Variables are already set,
                    # no need to set them again, just return the state
                    yield state

    ...
    
    
class FileSystemMock(FileSystem):
    
    ...
    
    def contained_items(self, folder_binding):
        if folder_binding.value.name in self.items:
            for item in self.items.items():
                if str(pathlib.PurePath(item[0]).parent) == folder_binding.value.name:
                    yield item[1]

        else:
            raise MessageException("notFound", [folder_binding.variable.name])

~~~

Unfortunately, this means any helper that returns an error message needs to have the variable passed to it, which makes those helpers a little messier. However, it is much cleaner to centralize the error reporting code and have some extra arguments passed than the alternative: to catch errors that can happen all throughout the predications and return the errors there.  

Notice that the `FileSystemMock` class raises an `MessageException` exception when a object is not found. This is a special exception designed to be reported to the user. It has all the information needed by the system to report a nice error, using variable names, etc. Without code to convert the exception to user text, however, the system will just crash. Let's add that code:

~~~
    def _call_predication(self, state, predication):

        ...
        
            # If a MessageException happens during execution,
            # convert it to an error
            try:
                # You call a function "pointer" and pass it arguments
                # that are a list by using "function(*function_args)"
                # So: this is actually calling our function (which
                # returns an iterator and thus we can iterate over it)
                success = False
                for next_state in function(*function_args):
                    success = True
                    yield next_state

            except MessageException as error:
                self.report_error(error.message_object())
~~~

The code is deep in the system where predications are called. By putting the code there, we can just assume that a predication has failed if it gets an exception and, if it is a `MessageException`, convert it to a user-reportable error.

By passing variable context to helpers, and supporting converting `MessageExceptions` to user errors, we can allow helper functions to `raise` an error and have it be reported, without having to do a lot of special case handling in the predications themselves.

> Comprehensive source for the completed tutorial is available [here](https://github.com/EricZinda/Perplexity).