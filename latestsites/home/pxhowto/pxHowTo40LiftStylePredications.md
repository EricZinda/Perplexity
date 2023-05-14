{% raw %}## Predications with Multiple X Arguments: Lift-Style Predications
Not all words are associative with sets like "in" from the previous section: The verb "to lift" interprets sets vs, individuals as very different things.  For example:

```
Students lifted a table.
```
...*could* mean: 
1. Two students (together) lifted a table (at the same time)
2. Two students (separately) lifted a (different) table

This is a case where the prediction for "lift":

```
_lift_v_cause(e1,x1,x2)
```

... can't just check if each value of `x1` is lifting a value in `x2` and assume that means they are all also lifting alone or together.  Lifting together means something different, and thus, unlike "in", all combinations *do* need to be checked. There is a different helper that will do the logic for this scenario: `lift_style_predication()`. In contrast to `in_style_predication()`, the check functions need to be prepared for sets with more than one item and check if they are working *together*:

```
@Predication(vocabulary, names=["_lift_v_cause"])
def lift(state, e_introduced_binding, x_actor_binding, x_size_binding):
    def check_items_lifting_items(item1, item2):
        return is_lifting(item1, item2)
    
    def all_item1s_lifting_item2s(item2):
        yield from all_lifting(item2)

    def all_item2s_being_lifted_by_item1s(item1):
        yield from all_being_lifted(item1)

    yield from lift_style_predication(state, x_actor_binding, x_size_binding, 
                                      check_items_lifting_items, all_item1s_lifting_item2s, all_item2s_being_lifted_by_item1s)
```

So, `lift_style_predication()` works very much like the `in_style_predication()` from the previous section but calls the check function with sets.  

### Declaring Arguments that Understand with Sets > 1 item
As written, however, these check functions will *still* only get called with a single item. That is because the helper functions won't go through the work to generate all combinations unless a predication declares that they might use it. It is just too expensive to calculate if it will be thrown away.  To do this, we need to declare which arguments semantically understand sets of more than one by adding information to the `@Predication` declaration, like this:

```
@Predication(vocabulary, names=["_lift_v_cause"], arguments=[("e",), ("x", ValueSize.all), ("x", ValueSize.all)])
def lift(state, e_introduced_binding, x_actor_binding, x_size_binding):
    def check_items_lifting_items(item1, item2):
        return is_lifting(item1, item2)
    
    def all_item1s_lifting_item2s(item2):
        yield from all_lifting(item2)

    def all_item2s_being_lifted_by_item1s(item1):
        yield from all_being_lifted(item1)

    yield from lift_style_predication(state, x_actor_binding, x_size_binding, 
                                      check_items_lifting_items, all_item1s_lifting_item2s, all_item2s_being_lifted_by_item1s)
```

Adding the `arguments=[]` list to `@Predication` tells the engine that we want to override the defaults for arguments and declare them ourselves.  The default for all arguments is to only have single values since that is *much* faster.  Only predications which specially process more than one arguments should ask for them. The declaration for `lift` asks for them by setting `ValueSize.all` on both `x` arguments.

Other options for `ValueSize` are: `exactly_one` (the default) and `more_than_one`. `more_than_one` can be used when an argument only makes sense for more than one individual to be doing it. One example is the verb "met".

Last update: 2023-05-13 by EricZinda [[edit](https://github.com/EricZinda/Perplexity/edit/main/docs/pxHowTo/pxHowTo40LiftStylePredications.md)]{% endraw %}