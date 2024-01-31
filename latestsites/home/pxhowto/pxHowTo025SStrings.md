{% raw %}## S-String Overview
As described in the [Words in Failures topic](https://blog.inductorsoftware.com/Perplexity/home/pxint/pxint0120ErrorsConceptualFailures), errors or messages to the user often need to include a representation of some noun that the user said. For example, a user might say, "give me a long brown towel".  Here's one tree for that phrase:

```
                                             ┌──── _towel_n_1(x8)
                                             │ ┌── _brown_a_1(e19,x8)
                                 ┌────── and(0,1,2)
               ┌────── pron(x9)  │               └ _long_a_2(e18,x8)
pronoun_q(x9,RSTR,BODY)          │
                    └─ _a_q(x8,RSTR,BODY)
                                      │                 ┌────── pron(x3)
                                      └─ pronoun_q(x3,RSTR,BODY)
                                                             └─ _give_v_1(e2,x3,x8,x9)
```
We'd like to have the code for `_give_v_1` be able to say "There isn't {whatever `x8` is} in the system" without having to write a bunch of non-trivial code to decode the tree and turn it into English. To help, Perplexity has a built-in way to do this. In fact, it provides a very general way to build responses by providing a template. It is called an "s-string" and works analogously to [f-strings](https://docs.python.org/3/tutorial/inputoutput.html) in Python.

At its most basic level, s-strings can be used like an f-strings to do replacement of variables in a string like this:
```
>>> value1 = "hello"
>>> print(
          s("The value is {*value1}")
          )

The value is hello
```

`s()` is the s-string function and it takes a string that will be processed. Anything enclosed in `{}` in the string will be converted to text by the system. Above we've used `*value1` as the value to be replaced.  The `*` means "put whatever is in `value1` in the string as-is".

S-strings also understand how MRS trees work and can convert a DELPH-IN variable like `x8` in the above example into the English that represents it. To do this it also requires passing the MRS tree that should be decoded. This is always available in a special `'tree'` variable in the `state` argument of a predication. It can be accessed by calling `state.get_binding('tree').value[0]`. 

So, we could print a message from the `_give_v_1` predication above like this:

```
@Predication(vocabulary, names=["_give_v_1"])
def give_v_1(state, e_introduced, x_giver_binding, x_what_binding, x_receiver_binding):
   print(
        s("There isn't {x_what_binding.variable.name} in the system", state.get_binding('tree').value[0])
    )
```

A term in `{}` without a `*` in front like: `{x_variable_binding.variable.name}` tells the system to interpret the expression as containing a DELPH-IN variable name. The system will convert the DELPH-IN variable to English by decoding the tree passed to `s()`, and looking for all the terms that modify the variable. Then it will put that English representation in the string.

Using our example of "Give me a long brown towel" with the code for `give_v_1()` above, the system will print out:

```
There isn't a long brown towel in the system
```

Note that the system includes the quantifier the user used for `x8`, which is "a" in this case, because we didn't specify one inside the `{}`.  That means if the user said "give me the beautiful towels", we'd get this printed out:

```
There isn't the beautiful towels in the system
```

Which isn't quite right. We really want something like "There aren't any beautiful towels", which we can generate like this:

```
@Predication(vocabulary, names=["_give_v_1"])
def give_v_1(state, e_introduced, x_giver_binding, x_what_binding, x_receiver_binding):
   print(
        s("There aren't any {bare x_what_binding.variable.name:pl}", state.get_binding('tree').value[0])
    )
```
By using `{bare x_what_binding.variable.name:pl}`, we've told the system to get rid of the quantifier (by using `bare`) and to put it into plural form (by using `:pl`).  Now, we get a better result:

```
"give me the beautiful towels" -> There aren't any beautiful towels
"give me a towel on the chair" -> There aren't any towels on the chair
```

Sometimes you need a word in the phrase to match the plurality of a word in the MRS. Let's say we want to print the message, "[what the user said] is in the cupboard". We could do that by writing this code:

```
@Predication(vocabulary, names=["_give_v_1"])
def give_v_1(state, e_introduced, x_giver_binding, x_what_binding, x_receiver_binding):
   print(
        s("{x_what_binding.variable.name} {'is':<x_what_binding.variable.name} in the cupboard", state.get_binding('tree').value[0])
    )
```

For this version:
- `{x_what_binding.variable.name}` says "use the existing quantifier and plurality as the user said it" like our first example.
- `{'is':<x_what_binding.variable.name}` says "make the word `'is'` match the English represented by the DELPH-IN variable in `x_what_binding.variable.name`"

Here are some examples of it in use:

```
give me the towels        -> the towels are in the cupboard
give me a towel           -> a towel is in the cupboard
give me some clean towels -> some clean towels are in the cupboard
```

# S-String Reference

Elements in an s-string have the format `{determiner value:pluralization@meaning_at_index}`. The below sections go through each section of the format and describe all of the valid values.

## Value
> s-string format: `{determiner value:pluralization@meaning_at_index}`

The only required part of an s-string is: `value`:

- `value` is interpreted as a Python variable that contains a string representing a DELPH-IN variable such as `"x8"`
- `*value` is interpreted as a Python variable that can contain any text such as `"dog"`, `"is"` or `"the frying pan from my room"`
- `"value"` or `'value'` is interpreted as a raw string

Note: When using the `*value` or `"value"` forms, any text can be used and will be inserted into the string. However, if `pluralization` is also being used (see below) to get the word transformed into a specific plural form, the text must be a singular noun form.

## Determiner
> s-string format: `{determiner value:pluralization@meaning_at_index}`

Put one of the following as `determiner` to force that type of article to be used instead of what the user said:
- `a` or `an` to include an indefinite article. Either works and will be changed to match the text when the string is evaluated.
- `the` to include a definite article
- `bare` to remove all articles

Providing no `determiner` uses the determiner (if any) that was in the user's phrase.

Examples:
```
User says 'the lively party':

{value}      -> "the lively party"
{an value}   -> "a lively party"
{bare value} -> "lively party
```

## Capitalization
> s-string format: `{determiner value:pluralization@meaning_at_index}`

To capitalize the generated text, capitalize `determiner`, like `{The value}` or `{Bare value}`

```
User says 'the lively party':

{An value} -> "A lively party"
{Bare value} -> "Lively party"
```

## Pluralization
> s-string format: `{determiner value:pluralization@meaning_at_index}`

`pluralization` specifies how to shape the plural of the item represented by `value`. To force the item into plural or singular form, use `:` followed by:
- `sg` : singular
- `pl` : plural
- (no text) : leave as-is
- `<delphin_variable`: match the singular or plural of whatever the DELPH-IN variable in `delphin_variable` represents
- `<*noun_variable`: match the singular or plural of whatever *noun* is contained directly in `noun_variable`
- `<"noun value"`: match the singular or plural of a *noun* string literal

Note that for pluralization to work when `value` is not a DELPH-IN variable:
- `*value` must be a *singular form* word such as `"dog"` or `"is"`
- `"value"` or `'value'` must be a raw string that is similarly in *singular form*

### Meaning at Index
> s-string format: `{determiner value:pluralization@meaning_at_index}`

The meaning of a DELPH-IN variable in an MRS tree depends on where in the tree it gets evaluated.  `@meaning_at_index` tells the system to convert a DELPH-IN variable to what its meaning would be after evaluating all the predications up to, but not including, the predication at that index. The index represents the depth-first evaluation order the system uses, starting at zero.

`meaning_after_index` can be a numeric literal like `5`, or it can be a local variable like `x`.

For example, the tree below for, "The dirty car is yellow" has the predication indexes represented before each predication:

```
                         ┌── 1:_car_n_1(x3)
             ┌────── and(0,1)
             │             └ 2:_dirty_a_1(e8,x3)
0:_the_q(x3,RSTR,BODY)
                  └─ 3:_yellow_a_1(e2,x3)
```
Assuming a variable `x3_variable = 'x3'` then we can generate the value of `x3` at each point in the tree like this:
0. `{x3_variable:@0}` means before the tree starts: `"thing"`
1. `{x3_variable:@1}` means after `_the_q`: `"the thing"`
2. `{x3_variable:@2}` means after `_car_n_1` is: `"the car"`
3. `{x3_variable:@3}` means after `__dirty_a_1` is: `"the dirty car"`
4. `{x3_variable:@4}` means after the tree is finished: `"the dirty yellow car"`

If no `@meaning_at_index` is provided, the default is to generate the tree only to the point right after where the variable is introduced. That would be `@2` above. 

To facilitate generating errors when predications are being executed, `@meaning_at_index` can also be set automatically if special values of `value` are used. The special values must be a Python `list` in one of these forms:
- `["AtPredication", TreePredication, variable]`: Evaluate `variable`'s English meaning at the index from the predication object in `TreePredication`
- `["AfterFullPhrase", variable]`: Evaluate `variable`'s English meaning after the whole tree is evaluated

For example, if we have the following code:
```
@Predication(vocabulary, names=["_give_v_1"])
def give_v_1(state, e_introduced, x_giver_binding, x_what_binding, x_receiver_binding):
  after_tree = ["AfterFullPhrase", x_what_binding.variable.name]
  print(
        s("{after_tree} in the cupboard", state.get_binding('tree').value[0])
        )
```

And say the phrase "give me the blue dog", the code would print:

```
the blue dog is in the cupboard
```

Since that is what `x` means after the entire phrase is done.

If we instead implement the `_the_q` predication like this:
```
@Predication(vocabulary, names=["_the_q"])
def the_q(state, x_variable_binding, h_rstr, h_body):
  at_predication = ["AtPredication", h_rstr[1], x_variable_binding.variable.name]
  print(
        s("{at_predication} is in the cupboard", state.get_binding('tree').value[0])
        )
```

And say the phrase "give me the blue dog", we would get:

```
the dog is in the cupboard
```

Since we have chosen to get the representation of the variable after only the first item in the `_the_q` `RSTR` has been evaluated.  The `RSTR` for "the blue dog" would be a conjunction of `[_dog_n_1(x8), _blue_a_1(e18,x8)]` like this:

```
                                               ┌── _dog_n_1(x8)
                                   ┌────── and(0,1)
               ┌────── pron(x9)    │             └ _blue_a_1(e18,x8)
pronoun_q(x9,RSTR,BODY)            │
                    └─ _the_q(x8,RSTR,BODY)
                                        │                 ┌────── pron(x3)
                                        └─ pronoun_q(x3,RSTR,BODY)
                                                               └─ _give_v_1(e2,x3,x8,x9)
```

So asking for `["AtPredication", h_rstr[1], x_variable_binding.variable.name]` sets the second element of the `RSTR` to be the `@meaning_at_index`, which skips `_blue_a_1`.

Last update: 2023-06-01 by EricZinda [[edit](https://github.com/EricZinda/Perplexity/edit/main/docs/pxHowTo/pxHowTo025SStrings.md)]{% endraw %}