{% raw %}# Manipulating Conceptual References
Let's now implement something that really has to deal with a concept as a *thing*: creating a file.

Let's say we want to support phrases like:

```
create a file
create a text file
create a test file containing "Hello World"
create a test file containing "Hello World" with read-only permissions
etc.
```

Everything to the right of "create a" is a [referring expression](https://en.wikipedia.org/wiki/Referring_expression), basically an arbitrarily complex noun phrase that describes or "refers to" something. When that "something" is actually in the world, the techniques we have gone through so far are sufficient to handle it. But in creating files, we are describing something that does not yet exist, so writing predications that find objects in the world and return them won't work. We need a different approach.

The Perplexity `Concept` object gives us a direction, but we'll need to enhance it. We will create a richer kind of `Concept` object that can hold a representation of these "conceptual" referring expressions and build predications that use them.

### Creating a File
Below is the built-in `Concept` object. Its default implementation just stores a single string from the constructor called `sort_of` which represents the sort of concept it is.  Period. It doesn't do anything with it. As far as Perplexity is concerned, the only part of it that gets used is the `value_type` property which returns `VariableValueType.concept`.  This tells Perplexity "I am a concept, treat me as an opaque blob".  The rest of the methods are there to support equality and membership in dictionaries and are used by things like the Python `dict` object:

```
class Concept(object):
    def __init__(self, sort_of):
        # This is a set so it is more easily comparable since order doesn't matter
        self._sort_of_criteria = set([sort_of]) if sort_of is not None else set()
        self._hash = None

    def __repr__(self):
        return f"Concept({','.join(self._sort_of_criteria)})"

    # The only required property is that objects which compare equal have the same hash value
    # But: objects with the same hash aren't required to be equal
    # It must remain the same for the lifetime of the object
    def __hash__(self):
        if self._hash is None:
            # TODO: Make this more efficient
            self._hash = hash(tuple(self._sort_of_criteria))

        return self._hash

    def __eq__(self, other):
        if isinstance(other, Concept) and self.__hash__() == other.__hash__():
            return True

    def value_type(self):
        return VariableValueType.concept
```

Let's start by implementing "create a file" using this class.  Looking at the MRS:

```
? create a file
I don't know the words: create

? /show
User Input: create a file
4 Parses

***** CHOSEN Parse #0:
Sentence Force: prop-or-ques
[ "create a file"
  TOP: h0
  INDEX: e2 [ e SF: prop-or-ques TENSE: tensed MOOD: indicative PROG: - PERF: - ]
  RELS: < [ _create_v_1<0:6> LBL: h1 ARG0: e2 ARG1: i3 ARG2: x4 [ x PERS: 3 NUM: sg IND: + ] ]
          [ _a_q<7:8> LBL: h5 ARG0: x4 RSTR: h6 BODY: h7 ]
          [ _file_n_of<9:13> LBL: h8 ARG0: x4 ARG1: i9 ] >
  HCONS: < h0 qeq h1 h6 qeq h8 > ]
```

... we can see that we'll need to implement a new version of `_file_n_of` that creates a `Concept` instead of actual files as the current one does. The base `Concept` class is enough for this. Our implementation will be an exact copy of the `_command_n_1` implementation we built in the [Non-logical meaning section](https://blog.inductorsoftware.com/Perplexity/home/pxhowto/pxHowTo100NonlogicalMeaning), just replacing the string "command" with "file":

```
@Predication(vocabulary, names=["_file_n_of"])
def file_n_of_concept(context, state, x_binding, i_binding):
    def bound_variable(value):
        if isinstance(value, Concept) and value == Concept("file"):
            return True
        else:
            context.report_error(["valueIsNotX", value, x_binding.variable.name])
            return False

    def unbound_variable():
        yield Concept("file")

    yield from combinatorial_predication_1(context,
                                           state,
                                           x_binding,
                                           bound_variable,
                                           unbound_variable)
```

Next we'll implement `_create_v_1` exactly like we implemented `_delete_v_1` in the [action verbs section](https://blog.inductorsoftware.com/Perplexity/home/pxhowto/pxHowTo070ActionVerbs). It will use a new operation (which we'll implement next) called `CreateOperation` to do the creating.  For now, we'll just hard code the name of the file to be "newfile":

```
@Predication(vocabulary, names=["_create_v_1"])
def create_v_1_comm(context, state, e_introduced_binding, x_actor_binding, x_what_binding):
    def criteria(value):
        # Only allow creating conceptual files
        if isinstance(value, Concept) and value == Concept("file"):
            return True

        else:
            context.report_error(["cantDo", "create", x_what_binding.variable.name])

    def unbound_what():
        context.report_error(["cantDo", "create", x_what_binding.variable.name])

    for success_state in individual_style_predication_1(context,
                                                        state,
                                                        x_what_binding,
                                                        criteria,
                                                        unbound_what,
                                                        ["cantXYTogether", "create", x_what_binding.variable.name]):
        object_to_create_binding = success_state.get_binding(x_what_binding.variable.name)
        operation = CreateOperation(object_to_create_binding, "newfile")
        yield success_state.apply_operations([operation])
```

And finish by implementing `CreateOperation`. It does the actual creating by calling our file system object (the code for that is not shown):
```
class CreateOperation(object):
    def __init__(self, binding_to_create, file_name):
        self.binding_to_create = binding_to_create
        self.file_name = file_name

    def apply_to(self, state):
        state.file_system.create_item(self.binding_to_create, self.file_name)
```

Now we can run it:

```
? create a file
Done!
```

Not very exciting and since we don't have a way to list files, we'll have to trust that it works or examine in the debugger.

To get this far, we've used concepts we've already explained in previous sections that should be relatively familiar. Next, we'll cover some new ground.

### A Richer Concept
Let's now tackle the next phrase from our list at the beginning of this section: "create a text file". As always, we'll start by examining the MRS to see what predications we need to implement:

```
? create a text file
I don't know the words: text, text file

? /show
User Input: create a text file
4 Parses

***** CHOSEN Parse #1:
Sentence Force: comm
[ "create a text file"
  TOP: h0
  INDEX: e2 [ e SF: comm TENSE: pres MOOD: indicative PROG: - PERF: - ]
  RELS: < [ pronoun_q<0:18> LBL: h4 ARG0: x3 [ x PERS: 2 PT: zero ] RSTR: h5 BODY: h6 ]
          [ pron<0:18> LBL: h7 ARG0: x3 ]
          [ _create_v_1<0:6> LBL: h1 ARG0: e2 ARG1: x3 ARG2: x8 [ x PERS: 3 NUM: sg IND: + ] ]
          [ _a_q<7:8> LBL: h9 ARG0: x8 RSTR: h10 BODY: h11 ]
          [ compound<9:18> LBL: h12 ARG0: e13 [ e SF: prop TENSE: untensed MOOD: indicative PROG: - PERF: - ] ARG1: x8 ARG2: x14 ]
          [ udef_q<9:13> LBL: h15 ARG0: x14 RSTR: h16 BODY: h17 ]
          [ _text_n_of<9:13> LBL: h18 ARG0: x14 ARG1: i19 ]
          [ _file_n_of<14:18> LBL: h12 ARG0: x8 ARG1: i20 ] >
  HCONS: < h0 qeq h1 h5 qeq h7 h10 qeq h12 h16 qeq h18 > ]

-- CHOSEN Parse #1, CHOSEN Tree #0: 

                                                                  ┌── _file_n_of(x8,i20)
             ┌────── _text_n_of(x14,i19)                          │
             │                                        ┌────── and(0,1)
udef_q(x14,RSTR,BODY)               ┌────── pron(x3)  │             │
                  │                 │                 │             └ compound(e13,x8,x14)
                  └─ pronoun_q(x3,RSTR,BODY)          │
                                         └─ _a_q(x8,RSTR,BODY)
                                                           └─ _create_v_1(e2,x3,x8)
```
There are 2 new predications to implement: `_text_n_of` and `compound`.  Basically, the ERG is creating the concept of "text" and the concept of "file" and combining them together with the `compound` predication. `_text_n_of` will end up looking just like `_file_n_of` above:

```
@Predication(vocabulary, names=["_text_n_of"])
def text_n_of_concept(context, state, x_binding, i_binding):
    def bound_variable(value):
        if isinstance(value, Concept) and value == Concept("text"):
            return True
        else:
            context.report_error(["valueIsNotX", value, x_binding.variable.name])
            return False

    def unbound_variable():
        yield Concept("text")

    yield from combinatorial_predication_1(context,
                                           state,
                                           x_binding,
                                           bound_variable,
                                           unbound_variable)
```

Next up is `compound(e13,x8,x14)`. 

The `x8` in `compound` is always the "base object", i.e. "seat" in "bicycle seat", "food" in "baby food", etc. 

`x14` is the modifier which filters down what *kind* of base object we are discussing. 

If we were working with object instances (and not concepts) we would simply do a check to see if `x8` is an "`x14` kind of object" and succeed or not. But, because we are building up a *concept*, we actually need to *modify* the value in `x8` to include that additional description so that downstream predications see a concept that is a "text" kind of "file". We need to enhance the "Concept" object to support this. Since Perplexity doesn't care about the `Concept` object, per se, and only cares that the object has the `value_type` method on it, we can just create our own `RichConcept` object and use that.

To do this, we need start building up a simple way of describing things. We'll describe a referred-to-thing with a list of "criteria", which are simply "relationships" and "values".  For example:
```
Description of "text file":
    object "is_a" "file"
    object "has_adjective" "text"
```

Here is the implementation of that:

```
class RichConcept:
    def __init__(self, is_a=None):
        self.criteria = [] if sort_of is None else [("is_a", sort_of)]
        self._hash = None

    def __repr__(self):
        return f"RichConcept({[x for x in self.criteria]})"

    # The only required property is that objects which compare equal have the same hash value
    # But: objects with the same hash aren't required to be equal
    # It must remain the same for the lifetime of the object
    def __hash__(self):
        if self._hash is None:
            self._hash = hash(tuple(self.criteria))

        return self._hash

    def __eq__(self, other):
        if isinstance(other, RichConcept) and self.__hash__() == other.__hash__():
            return True

    def value_type(self):
        return VariableValueType.concept

    def add_criteria(self, relationship, value):
        self_copy = copy.deepcopy(self)
        self_copy.criteria.append((relationship, tuple))
        self_copy._hash = None
        return self_copy
```

And with that in place we can tackle `compound`.  The way things are currently implemented, for the phrase "create a text file", `compound` will get called with its arguments set to:

```
compound(e13,x8,x14)
x8 = RichObject("file")   # object "is_a" "file"
x14 = RichObject("text")  # object "is_a" "text"
```

This isn't quite right. A text file "is_a" file, but it "has" text, it is not "text". 

The problem is in how we've interpreted the predications `_text_n_of` and `_file_n_of`.  Normally, these predications should be `true` for objects that "are" (i.e. "is_a") that kind of thing. That is how they are implemented and that is the kind of `Concept` being returned by them at the moment. But when used with `compound`, the 2nd argument is used more like an adjective than a noun.  Consider "baby food". A jar of baby food is *not* a baby. "Baby" is being used as an adjective.  

The problem is that `text_n_of` (or "baby") get called without knowing this is how they'll be used. So, we can either write two different *interpretations* for all noun predications: one interpreting as "is_a" and one interpreting as "has_adjective" and then compound will always only be `true` for the second.  Or: we can have the `compound` predication do some special magic to interpret nouns as adjectives.

Since we don't have other predications that need to treat nouns as adjectives, for now we'll centralize the code in `compound` to save work. We will add a method to our `RichConcept` class called `add_adjective_concept`. This method will simply convert "is_a" relationships to "has_adjective" relationships and then add to the base object:

```
class RichConcept:
    
    ...
    
    def add_criteria(self, relationship, value):
        self_copy = copy.deepcopy(self)
        self_copy.criteria.append((relationship, tuple))
        self_copy._hash = None
        return self_copy

    def add_adjective_concept(self, other_concept):
        self_copy = copy.deepcopy(self)
        for criteria in other_concept.criteria:
            if criteria[0] == "is_a":
                self_copy.criteria.append(("has_adjective", criteria[1]))
            else:
                self_copy.criteria.append(criteria)
        self_copy._hash = None
        return self_copy
```

This makes `compound` easy to write. Due to the way it is used in English, it will always have both arguments bound: there isn't a way to make a compound word where you are asking what the first part is that will generate this predication. So, all we need to do is use our new method to combine the second argument into the first and yield that as the new first argument:

```
@Predication(vocabulary,
             names=["compound"])
def compound_concept(context, state, e_introduced_binding, x_base_binding, x_modifier_binding):
    # Only support concepts
    # Both arguments will always be bound for compound 
    # so we don't need to check unbound cases. Furthermore, the value will always be
    # a single value due to the way it is parsed, so we only need to check the first value
    if not isinstance(x_base_binding.value[0], RichConcept) or not isinstance(x_modifier_binding.value[0], RichConcept):
        context.report_error(["formNotUnderstood"])
        return
    
    compound_value = x_base_binding.value[0].add_adjective_concept(x_modifier_binding.value[0])
    yield state.set_x(x_base_binding.variable.name, (compound_value, ))   
```

Note the use of the special error "formNotUnderstood" if the predication is called with a value that is not a `RichConcept`. This tells the system, "this predication is not appropriate for these values". It is neither `true` nor `false`. It allows the system to give better errors.

The final code we need to write is in the `CreateOperation` and underlying filesystem objects that actually do the work.

`CreateOperation` doesn't need to change since it just passes along the values:
```
class CreateOperation(object):
    def __init__(self, binding_to_create, file_name):
        self.binding_to_create = binding_to_create
        self.file_name = file_name

    def apply_to(self, state):
        state.file_system.create_item(self.binding_to_create, self.file_name)
```

The real work happens in the `FileSystem` object that haven't really gone through.  The pertinent code is below.  It does the work of finding the one adjective that describes the type of file to creating and failing if there is none or more than one.  Obviously this code could be made more robust, but that isn't what we're focused on here. This is just a simple implementation:

```
class FileSystem:
    ...
    
    def get_file_type(self, concept):
        file_type = None
        for criteria in concept.criteria:
            if criteria[0] == "has_adjective":
                if file_type is None:
                    file_type = criteria[1]
                else:
                    # More than one type described, fail
                    return None
        
        return file_type
```

If we now run a test, we get this:

```
? create a text file
[7, ['cantDo', 'create', 'x8'], 0]
```

(We haven't added to code to make a nice error yet ...)

Hmmm. What happened here? Let's dig in.

### Logical Entailment

The problem is in the implementation of `_create_v_1`.  It checks to see if its argument `== RichConcept("file")`, but the `Concept` is no longer simply a file, it is a `RichConcept([('is_a', 'file'), ('has_adjective', 'text')])`, so it fails:

```
@Predication(vocabulary, names=["_create_v_1"])
def create_v_1_comm(context, state, e_introduced_binding, x_actor_binding, x_what_binding):
    def criteria(value):
        # Only allow creating conceptual files
        if isinstance(value, RichConcept) and value == RichConcept("file"):
            return True

        else:
            context.report_error(["cantDo", "create", x_what_binding.variable.name])
    
    ...
```

As far as this predication is concerned, we don't care what *type* of file the user asked to create, that will be dealt with elsewhere.  We just care that it is, at its core, a *file*.  Here, we can appeal to a concept from logic called "logical consequence" or ["logical entailment"](https://en.wikipedia.org/wiki/Logical_consequence).  Really, you can think of it as "implies".  Being a "text file" will always mean it is also a "file". So, "text file" *entails* "file" or "text file" *implies* "file". In this function we want to check for *entailment* of "file", not equality.

Now, proving entailment is an active area of research. It is a hard problem in the general case. But we don't have the general case here, we have a very limited vocabulary and set of scenarios.  We can therefore just say that something entails something else as long as they both "is_a" the same thing:

Let's add a method to our `Concept` object to do that (the last method below):

```
class RichConcept:
    def __init__(self, is_a=None):
        self.criteria = [] if is_a is None else [("is_a", is_a)]
        self._hash = None

    def __repr__(self):
        return f"RichConcept({[x for x in self.criteria]})"

    # The only required property is that objects which compare equal have the same hash value
    # But: objects with the same hash aren't required to be equal
    # It must remain the same for the lifetime of the object
    def __hash__(self):
        if self._hash is None:
            self._hash = hash(tuple(self.criteria))

        return self._hash

    def __eq__(self, other):
        if isinstance(other, RichConcept) and self.__hash__() == other.__hash__():
            return True

    def value_type(self):
        return VariableValueType.concept

    def add_criteria(self, relationship, value):
        self_copy = copy.deepcopy(self)
        self_copy.criteria.append((relationship, tuple))
        self_copy._hash = None
        return self_copy

    def add_adjective_concept(self, other_concept):
        self_copy = copy.deepcopy(self)
        for criteria in other_concept.criteria:
            if criteria[0] == "is_a":
                self_copy.criteria.append(("has_adjective", criteria[1]))
            else:
                self_copy.criteria.append(criteria)
        self_copy._hash = None
        return self_copy

    def entails(self, other_concept):
        for criteria in self.criteria:
            if criteria[0] == "is_a":
                for other_criteria in other_concept.criteria:
                    if other_criteria[0] == "is_a" and other_criteria[1] == criteria[1]:
                        return True

        return False
```

Then, fix up our `_create_v_1` predication to use `entails` instead of `==`:

```
@Predication(vocabulary, names=["_create_v_1"])
def create_v_1_comm(context, state, e_introduced_binding, x_actor_binding, x_what_binding):
    def criteria(value):
        # Only allow creating conceptual files
        if isinstance(value, RichConcept) and value.entails(RichConcept("file")):
            return True

        else:
            context.report_error(["cantDo", "create", x_what_binding.variable.name])

    def unbound_what():
        context.report_error(["cantDo", "create", x_what_binding.variable.name])

    for success_state in individual_style_predication_1(context,
                                                        state,
                                                        x_what_binding,
                                                        criteria,
                                                        unbound_what,
                                                        ["cantXYTogether", "create", x_what_binding.variable.name]):
        object_to_create_binding = success_state.get_binding(x_what_binding.variable.name)
        operation = CreateOperation(object_to_create_binding, "newfile")
        yield success_state.apply_operations([operation])
```

Now if we run our test:

```
? create a text file
Done!
```

### Other Referring Expressions
Let's go back to our example phrases from the beginning:

```
create a file
create a text file
create a test file containing "Hello World"
create a test file containing "Hello World" with read-only permissions
etc.
```

We got through the first 2. Hopefully, now you can see how the others are simply adding more and more criteria onto the `Concept`object and then implementing them when it is time to do the file creation.

Because we've done a lot in this section, here is all the new code we had to write:

```
@Predication(vocabulary, names=["_file_n_of"])
def file_n_of_concept(context, state, x_binding, i_binding):
    def bound_variable(value):
        if isinstance(value, RichConcept) and value == RichConcept("file"):
            return True
        else:
            context.report_error(["valueIsNotX", value, x_binding.variable.name])
            return False

    def unbound_variable():
        yield RichConcept("file")

    yield from combinatorial_predication_1(context,
                                           state,
                                           x_binding,
                                           bound_variable,
                                           unbound_variable)
                                           
                                           
@Predication(vocabulary, names=["_text_n_of"])
def text_n_of_concept(context, state, x_binding, i_binding):
    def bound_variable(value):
        if isinstance(value, RichConcept) and value == RichConcept("text"):
            return True
        else:
            context.report_error(["valueIsNotX", value, x_binding.variable.name])
            return False

    def unbound_variable():
        yield RichConcept("text")

    yield from combinatorial_predication_1(context,
                                           state,
                                           x_binding,
                                           bound_variable,
                                           unbound_variable)


@Predication(vocabulary,
             names=["compound"])
def compound_concept(context, state, e_introduced_binding, x_base_binding, x_modifier_binding):
    # Only support concepts
    # Both arguments will always be bound for compound
    # so we don't need to check unbound cases. Furthermore, the value will always be
    # a single value due to the way it is parsed, so we only need to check the first value
    if not isinstance(x_base_binding.value[0], RichConcept) or not isinstance(x_modifier_binding.value[0], RichConcept):
        context.report_error(["formNotUnderstood"])
        return

    compound_value = x_base_binding.value[0].add_adjective_concept(x_modifier_binding.value[0])
    yield state.set_x(x_base_binding.variable.name, (compound_value, ))
    

@Predication(vocabulary, names=["_create_v_1"])
def create_v_1_comm(context, state, e_introduced_binding, x_actor_binding, x_what_binding):
    def criteria(value):
        # Only allow creating conceptual files
        if isinstance(value, RichConcept) and value.entails(RichConcept("file")):
            return True

        else:
            context.report_error(["cantDo", "create", x_what_binding.variable.name])

    def unbound_what():
        context.report_error(["cantDo", "create", x_what_binding.variable.name])

    for success_state in individual_style_predication_1(context,
                                                        state,
                                                        x_what_binding,
                                                        criteria,
                                                        unbound_what,
                                                        ["cantXYTogether", "create", x_what_binding.variable.name]):
        object_to_create_binding = success_state.get_binding(x_what_binding.variable.name)
        operation = CreateOperation(object_to_create_binding, "newfile")
        yield success_state.apply_operations([operation])
        
        
class CreateOperation(object):
    def __init__(self, binding_to_create, file_name):
        self.binding_to_create = binding_to_create
        self.file_name = file_name

    def apply_to(self, state):
        state.file_system.create_item(self.binding_to_create, self.file_name)
        
        
class RichConcept:
    def __init__(self, is_a=None):
        self.criteria = [] if is_a is None else [("is_a", is_a)]
        self._hash = None

    def __repr__(self):
        return f"RichConcept({[x for x in self.criteria]})"

    # The only required property is that objects which compare equal have the same hash value
    # But: objects with the same hash aren't required to be equal
    # It must remain the same for the lifetime of the object
    def __hash__(self):
        if self._hash is None:
            self._hash = hash(tuple(self.criteria))

        return self._hash

    def __eq__(self, other):
        if isinstance(other, RichConcept) and self.__hash__() == other.__hash__():
            return True

    def value_type(self):
        return VariableValueType.concept

    def add_criteria(self, relationship, value):
        self_copy = copy.deepcopy(self)
        self_copy.criteria.append((relationship, tuple))
        self_copy._hash = None
        return self_copy

    def add_adjective_concept(self, other_concept):
        self_copy = copy.deepcopy(self)
        for criteria in other_concept.criteria:
            if criteria[0] == "is_a":
                self_copy.criteria.append(("has_adjective", criteria[1]))
            else:
                self_copy.criteria.append(criteria)
        self_copy._hash = None
        return self_copy

    def entails(self, other_concept):
        for criteria in self.criteria:
            if criteria[0] == "is_a":
                for other_criteria in other_concept.criteria:
                    if other_criteria[0] == "is_a" and other_criteria[1] == criteria[1]:
                        return True

        return False
        
class FileSysem:
    ...
    
    def get_file_type(self, concept):
        file_type = None
        for criteria in concept.criteria:
            if criteria[0] == "has_adjective":
                if file_type is None:
                    file_type = criteria[1]
                else:
                    # More than one type described, fail
                    return None

        return file_type
```

> Comprehensive source for the completed tutorial is available [here](https://github.com/EricZinda/Perplexity/tree/main/samples/hello_world)

Last update: 2024-10-25 by Eric Zinda [[edit](https://github.com/EricZinda/Perplexity/edit/main/docs/pxHowTo/pxHowTo120ConceptsReferringExpressions.md)]{% endraw %}