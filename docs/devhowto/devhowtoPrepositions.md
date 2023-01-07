## Prepositions (for both questions and commands)
So far, we've been building up the ability to evaluate an MRS against a software world model, but have only been using fragments of sentences like "a very large file". Now it is time to start understanding full sentences by adding verbs:


"put the file in the folder". The file is not yet in the folder but the MRS looks like it is.  The scopal argument

~~~
                  ┌───── _safe_n_1__x:x12
_the_q__xhh:x12,RSTR,BODY                 ┌───── _diamond_n_1__x:x4
                       └ _the_q__xhh:x4,RSTR,BODY                          ┌ _in_p_loc__exx:e11,x4,x12
                                               └ _put_v_1__eixh:e2,i3,x4,ARG3
~~~

In this case, `in_p_loc` is being treated as instructions for `put_v_1` to describe where it wants it to end up.  The scopal argument is needed because it needs a chance to describe the world that "could be" not one that "is"

"in_p_loc" has some obvious arguments that can be gathered "from the outside"
"directional" prepositions have more potential options we may need that really should just be generated "from the inside".

What happens with "put the file in every folder?"

> Comprehensive source for the completed tutorial is available [here](https://github.com/EricZinda/Perplexity).
