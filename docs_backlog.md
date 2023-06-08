- Switch the docs to use the term "scope-resolved MRS" instead of "well-formed tree" or "scope-resolved tree"
- [quote="trimblet, post:6, topic:915"]
    > A DELPH-IN parser like [ACE](http://sweaglesw.org/linguistics/ace/) will usually generate more than one MRS document representing the various high-level interpretations of a phrase. Each one contains a *list* of predicate-logic-like predications and not a *tree* like you’ll see in many natural language systems. That’s because it is *underspecified* . Even though the parser has already done one level of interpretation on the phrase, there are still (usually) multiple ways to interpret *that* .
    
    Technically, the predications are stored as a bag, not a list. 
    [/quote]
    
    Got it: I'll switch list to bag. 
    
    [quote="trimblet, post:6, topic:915"]
    Also, I don’t think the *reason* the predications are stored as a bag is because of underspecification, but rather that there isn’t information that is stored in the ordering of predications and/or arcs between predications.
    
    While I’m not particularly opposed to this interpretation of “underspecified,” (though others might be), I think that usually an entire MRS isn’t referred to as underspecified. Instead, various components are underspecified. But, probably not a big deal if clarified in a footnote or introductory note or something.
    [/quote]
    
    Thanks: I'll change the phrasing to clarify that it is the connection between the predications that are underspecified, and, because the connections are underspecified, it is represented as a bag and not a tree.
    
- Old: Thinking of MRS variables as variables in a math equation can help: The MRS is effectively defining a formula with variables. If you pick variable values such that the MRS is true for a given world, then you have understood the meaning of the MRS in that world.

  New: Thinking of MRS variables as variables in a math equation can help: The MRS is effectively defining a formula with variables. One way to use the formula is to find the set of all variable values that make the MRS true in a given world. Those values, combined with the predications they are used in, provide a valuable tool for getting at the meaning of the original phrase.

- I haven’t read the whole thing, but the first thing that stood out was the use of “format” in the “MRS Format”. It is not a format, but a formalism; an abstract metalanguage for describing semantic structures and principles for their well-formedness. What I would call a “format” is one of the various serializations of a representation, such as SimpleMRS, Indexed MRS, MRS XML, etc.
- Ahh. OK, I think I get my confusion now, there are really two “linked structures” going on in a scope-resolved MRS: one which is (as Emily proposes) the “scope tree of a scope-resolved MRS”, and the other is a graph, which is there for both a scope resolved and an un-scope-resolved MRS (maybe called a “variable graph”?). Is there an official term for that graph that I should use?
  - https://delphinqa.ling.washington.edu/t/new-dev-docs-for-understanding-the-mrs-format/915/19
- which() needs to take wide scope
    - Fix the scope resolved trees docs?
