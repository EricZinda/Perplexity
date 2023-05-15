## Lift-Style Predications
Not all words are associative with sets like "in" from the [previous section](pxHowTo30InStylePredications): The verb "to lift" interprets sets vs. individuals as very different things.  For example:

~~~
Students lifted a table.
~~~
...*could* mean: 
1. Two students (together) lifted a table (at the same time)
2. Two students (separately) lifted a (different) table

This is a case where the prediction for "lift":

~~~
_lift_v_cause(e1,x1,x2)
~~~

... can't just check if each value of `x1` is lifting a value in `x2` and assume that means they are all also lifting separately or together.  Lifting together means something different, and thus, unlike "in", all combinations *do* need to be checked. There is a different helper that will do the logic for this scenario: `lift_style_predication_2()`. In contrast to `in_style_predication_2()`, the check functions need to be prepared for sets with more than one item and check if they are working *together*.

For this example, we'll assume that "Elsa" and "Seo-Yun" are lifting "table1" together:
~~~
@Predication(vocabulary, names=["_lift_v_cause"])
def lift(state, e_introduced_binding, x_actor_binding, x_item_binding):
    def check_items_lifting_items(item1, item2):
        if item1 == ("Elsa", "Seo-Yun") and len(item2) == 1 and item2[0] == "table1":
            return True
        else:
            report_error(["xIsNotYZ", x_actor_binding.variable.name, "lifting", x_item_binding.variable.name])

    def all_item1s_lifting_item2s(item2):
        if len(item2) == 1 and item2[0] == "table1":
            yield ("Elsa", "Seo-Yun")

    def all_item2s_being_lifted_by_item1s(item1):
        if item1 == ("Elsa", "Seo-Yun"):
            yield ("table1",)

    yield from lift_style_predication_2(state, x_actor_binding, x_item_binding,
                                        check_items_lifting_items, all_item1s_lifting_item2s,
                                        all_item2s_being_lifted_by_item1s)
~~~

So, `lift_style_predication_1()` works very much like the `in_style_predication_1()` from the [previous section](pxHowTo30InStylePredications) but calls the check function with sets.  

### Declaring Arguments that Understand Sets of More Than One Item
As written, however, these check functions will *still* only get called with a single item. That is because the helper functions won't go through the work to generate all combinations unless a predication declares that it will use a set if provided. It is too expensive to calculate if it will be thrown away.  

To declare that `lift()` actually interprets meaning in sets, we need to declare which arguments semantically understand sets of more than one by adding information to the `@Predication` declaration, like this:

~~~
@Predication(vocabulary,
             names=["_lift_v_cause"],
             arguments=[("e",), ("x", ValueSize.all), ("x", ValueSize.all)])
def lift(state, e_introduced_binding, x_actor_binding, x_item_binding):
    def check_items_lifting_items(item1, item2):
        if item1 == ("Elsa", "Seo-Yun") and len(item2) == 1 and item2[0] == "table1":
            return True
        else:
            report_error(["xIsNotYZ", x_actor_binding.variable.name, "lifting", x_item_binding.variable.name])

    def all_item1s_lifting_item2s(item2):
        if len(item2) == 1 and item2[0] == "table1":
            yield ("Elsa", "Seo-Yun")

    def all_item2s_being_lifted_by_item1s(item1):
        if item1 == ("Elsa", "Seo-Yun"):
            yield ("table1",)

    yield from lift_style_predication_2(state, x_actor_binding, x_item_binding,
                                        check_items_lifting_items, all_item1s_lifting_item2s,
                                        all_item2s_being_lifted_by_item1s)
~~~

Adding the `arguments=[]` list to `@Predication` tells the engine that we want to override the defaults for arguments and declare them ourselves.  The default for all arguments is to only have single values since that is *much* faster.  Only predications which specially process sets should ask for them. The declaration for `lift` asks for them by setting `ValueSize.all` on both `x` arguments.

Other options for `ValueSize` are: `exactly_one` (the default) and `more_than_one`. `more_than_one` can be used when an argument only makes sense for more than one individual to be doing it. One example is the verb "met".

## Running the Example
As is, we can't really run the table. We need to teach the system "students" and "tables" first.  This is easy enough using the approach we used in our [first topic](pxHowTo20ImplementAPredication) about files:

~~~
@Predication(vocabulary, names=["_student_n_of"])
def student_n_of(state, x_binding, i_binding):
    def bound_variable(value):
        if value in ["Elsa", "Seo-Yun"]:
            return True
        else:
            report_error(["notAThing", x_binding.value, x_binding.variable.name])
            return False

    def unbound_variable():
        yield "Elsa"
        yield "Seo-Yun"

    yield from combinatorial_style_predication_1(state, x_binding, bound_variable, unbound_variable)


@Predication(vocabulary, names=["_table_n_1"])
def table_n_1(state, x_binding):
    def bound_variable(value):
        if value in ["table1"]:
            return True
        else:
            report_error(["notAThing", x_binding.value, x_binding.variable.name])
            return False

    def unbound_variable():
        yield "table1"

    yield from combinatorial_style_predication_1(state, x_binding, bound_variable, unbound_variable)
~~~

Adding those, plus the implementation of `_lift_v_cause` above allows us to have this interaction:

~~~
python ./hello_world.py
? students are lifting a table
Yes, that is true.

? a student is lifting a table
There are more than a student

? which students are lifting the table
('Elsa', 'Seo-Yun')

? what is lifting a table?
I don't know the words: thing

? a student is large
a student is not large
~~~

A few things to note:

Because we defined `_lift_v_cause` to only be true when *both* students are lifting the table, we get the (mangled) error, "There are more than a student". This is trying to say "There is more than one student lifting a table". We'll go through how to fix the english on these in a future topic.  Probably we should add logic that allows either student lifting the table to be true as well, since people would expect that to be true.

We need to implement some more basic words like "thing" to start asking broarder questions about this scenario, but we can already ask some since the system implements "the" and "which"

Note that we can also use worlds like "large" from previous scenarios and they do work correctly (since we haven't said either student is large in the system).

Next we will tackle [event predications](pxHowTo50EventPredications) so that we can handle words like "very" and other modifiers.



