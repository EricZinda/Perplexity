## Responding by Using Sentence Force
So far, we've been building up the ability to evaluate an MRS against a software world model. Now it is time to start working through *types* of sentences and actually giving the answers people will expect from each type.

Let's look at the MRS for the sentence we've been working with so far, "A file is very large":
~~~
[ TOP: h0
INDEX: e2
RELS: < 
[ _a_q LBL: h4 ARG0: x3 [ x PERS: 3 NUM: sg IND: + ] RSTR: h5 BODY: h6 ]
[ _file_n_of LBL: h7 ARG0: x3 [ x PERS: 3 NUM: sg IND: + ] ARG1: i8 ]
[ _very_x_deg LBL: h1 ARG0: e9 [ e SF: prop TENSE: untensed MOOD: indicative PROG: - PERF: - ] ARG1: e2 ]
[ _large_a_1 LBL: h1 ARG0: e2 [ e SF: prop TENSE: pres MOOD: indicative PROG: - PERF: - ] ARG1: x3 ]
>
HCONS: < h0 qeq h1 h5 qeq h7 > ]


          ┌────── _file_n_of(x3,i8)
_a_q(x3,RSTR,BODY)    ┌── _very_x_deg(e9,e2)
               └─ and(0,1)
                        └ _large_a_1(e2,x3)
~~~
The *syntactic head* of a phrase indicates what the phrase is “about” or “built around”, and is usually a verb.  The MRS will represent the syntactic head of the phrase with one or more predications, possibly in a conjunction, and will point to the syntactic head using the `INDEX` field of the MRS. In this case, it is `INDEX = e2`. `e2` is introduced by `_large_a_1`.  Recall from [the events section](devhowtoEvents) that each (non-quantifier) predication *introduces* a variable that effectively represents it in the sentence. So, by pointing to a particular variable (`e2`), the MRS `Index` is indicating that the predication that introduces it (`large_a_1`) is the "syntactic head", or what the sentence is "about".

> The example sentence is thus *about* `_large_a_1`...which is not a verb.  This is a special case in DELPH-IN, where the common case of "being x" just drops the "being" and treats "x" as the verb.

Once you know the `index` (syntactic head) of a phrase, you can see what *type* of phrase it is by looking at the [*properties* of that variable](devhowtoMRS#variable-properties). This is the first time we've had to inspect variable properties, so lets dig in there a bit. 

You can see that, next to each argument in the MRS, there is a list of properties surrounded by `[]`. It looks like this for the `e2` argument of `_large_a_1`:

~~~
 e2 [ e SF: prop TENSE: pres MOOD: indicative PROG: - PERF: - ]
~~~

This is the list of properties for that variable. It provides various information about the kind of things that should be in that variable. Think of it as "metadata" about the variable or single argument predications for that variable.  The property we are interested in here is:
`SF: prop` ("sentence force": "proposition").  Every sentence is categorized into a *type*, indicated by the `SF` ("sentence force") property of its index variable:

- Proposition (`SF: prop`): "A file is large."
- Question (`SF: ques`): "Is a file large?", "Which file is large?", "A file is large?"
- Command (`SF: comm`): "Make a file large."

The "sentence force" of a sentence indicates what kind of response the user expects:
    
- User: "A file is large." -> "Yes, that is true"
- User: "Is a file large?" -> "Yes"
- User: "Which file is large?" -> "test1.txt"
- User: "Make a file large." -> "test1.txt is now large"

Note that these are all answers the user would expect if the statement worked.  All but the last would be very different if there were no large files in the system:

- User: "A file is large." -> "No, that isn't true"
- User: "Is a file large?" -> "No"
- User: "Which file is large?" -> "No files are large"
- User: "Make a file large." -> "test1.txt is now large"

In the [next few sections](devhowtoSimplePropositions) we'll work through how to handle the different types of sentences when they succeed. We'll end by talking about how to handle failures.