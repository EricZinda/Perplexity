{% raw %}## In-Style Predications
Logic gets more complicated when there is more than one `x` argument because there are many cases to handle. The ERG generates the following predication for "in" from "a file is in a folder":

```
_in_p_loc(e1,x1,x2)
```

Ignoring the event argument `e2` for the moment, there are two `x` arguments. The predication's job is to check whether `x1` is "in" `x2` (whatever that means in the application). Because arguments are tuples that can have more than one value (described in [the previous topic](https://blog.inductorsoftware.com/Perplexity/home/pxhowto/pxHowTo020ImplementAPredication)), the predication could be called with an argument that has two values, like this:

```
_in_p_loc(e1,(file1, file2),(folder1, ))
```

... which means "file1 and file2 are in folder1 *together*". For files, saying two files are in a folder "together" is no different than saying they are in a folder "separately". If `file1` is in `folder1` and `file2` is in `folder2`, then they are both in there separately *and* together. Note that the meaning of "in" in this case also doesn't *exclude* someone saying "together" or "separately". It is perfectly fine to say "Are file1 and file2 in folder2 together?", it just doesn't add anything to the meaning.

This observation allows us to separately check the files like this:

```
check: (file1,) in (folder1,)?
check: (file2,) in (folder1,)?
```

If those are both true, then this must be too (without having to check) since "in a folder together" is the same as "in a folder separatley":

```
check: (file1, file2) in (folder1,)?
```

This allows us to write a single function that can handle tuples of one or more items by simply implementing the one item case and calling it over and over.

As for the single `x` case from the [previous topic](https://blog.inductorsoftware.com/Perplexity/home/pxhowto/pxHowTo020ImplementAPredication), Perplexity has a helper function that performs the right logic and only requires the caller to implement the `check()` function for a single value, like this:

```
@Predication(vocabulary, names=("_in_p_loc"))
def in_p_loc(context, state, e_introduced_binding, x_actor_binding, x_location_binding):
    def check_item_in_item(item1, item2):
        return is_item_in_item(item1, item2)
    
    ...
                                          
    yield from in_style_predication_2(context,
                                      state, 
                                      x_actor_binding, 
                                      x_location_binding, 
                                      check_item_in_item, 
                                      ...)
```

[The example uses a placeholder function `is_item_in_item(item1, item2)` to do the checking since its logic is application specific.]

The function is called `in_style_predication_2()` because it uses the behavior of the word "in" as a template and has two `x` arguments.  Any predication that is like "in" (meaning that it doesn't have a different meaning for "together" or "separately" but is OK if they are said) can use this same helper to implement the logic efficiently.

#### Unbound Arguments
As discussed in the [previous topic](https://blog.inductorsoftware.com/Perplexity/home/pxhowto/pxHowTo020ImplementAPredication), arguments to a predication aren't always set (i.e. *bound*) as in the above example. When they are missing, the predication needs to yield all possible values for them that make the predication `true`.  

To support unbound arguments, `in_style_predication_2()` has two additional functions it supports: one for the first argument being unbound and another for the second. There is a final argument that is rarely used for when both are unbound. If that one isn't set, the system reports the system error `beMoreSpecific` since the user said something really broad like "what is in anything?"

Presumably the system we are building would have an efficient way to find "things in something else" (or vice versa) so the example below uses fake functions as placeholders:

```
@Predication(vocabulary, names=("_in_p_loc"))
def in_p_loc(context, state, e_introduced_binding, x_actor_binding, x_location_binding):
    def check_item_in_item(item1, item2):
        return is_item_in_item(item1, item2)
    
    def all_item1_in_item2(item2):
        yield from all_contained_in(item2)

    def all_item2_containing_item1(item1):
        yield from all_containing(item1)

    yield from in_style_predication_2(context, 
                                      state, 
                                      x_actor_binding, 
                                      x_location_binding, 
                                      check_item_in_item, 
                                      all_item1_in_item2, 
                                      all_item2_containing_item1)
```

Note that the two new functions need to *yield all alternatives* and not just return `true` or `false`, just like `combinatorial_style_predication_1()` did in the [previous topic](https://blog.inductorsoftware.com/Perplexity/home/pxhowto/pxHowTo020ImplementAPredication).

And, as with the first "check" function, `in_style_predication_2()` does all the work to make sure that the two unbound functions are only passed single values -- even if the incoming values are combinatorial or sets > 1 item.  

> Comprehensive source for the completed tutorial is available [here](https://github.com/EricZinda/Perplexity/tree/main/samples/hello_world)

Last update: 2024-10-24 by Eric Zinda [[edit](https://github.com/EricZinda/Perplexity/edit/main/docs/pxHowTo/pxHowTo030InStylePredications.md)]{% endraw %}