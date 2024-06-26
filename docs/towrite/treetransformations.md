Scenarios:
    I would like a table
               ┌────── _table_n_1(x11)
    _a_q(x11,RSTR,BODY)               ┌────── pron(x3)
                    └─ pronoun_q(x3,RSTR,BODY)                    ┌─ _like_v_1(e10,x3,x11)
                                           └─ _would_v_modal(e2,ARG1)
    I would like to leave
                                          ┌────── pron(x3)
                        ┌─ pronoun_q(x3,RSTR,BODY)                   ┌─ _leave_v_1(e13,x3,i14)
    _would_v_modal(e2,ARG1)                    └─ _like_v_1(e10,x3,ARG2)

Ideas:
    Allow tree transformations up front
    Treat them like separate trees that get executed first
    What is the programming model?
        specify a pattern to match
        specify what to replace it with
    Options:
        Write a simple rule that takes a predication/conj and returns a new one if it wants to replace it 
        OR
        Describe a pattern.  Have a match and capture approach, where the capture can be used elsewhere?
        How do we know when to apply?
            Ideally we trigger off of the root? Needs to be fast
        match_predicate(name, arg_types)
        {"would_v_modal": ["e", {"h": {"_like_v_1": ["e1", "x1", "x2"]}]}
        {"want_v_1": ["e1", "x1", "x2"]}
        OR
        "would_v_modal(e, _like_v_1$p1(e$e1, *$z1, x$x2)) -> _want_v_1($e1, $z1, $x2)"
        
        All the tranformers are in an order and run over the tree, one at a time, in order
        A transformer can only be active or not
        Walk the tree and see if the tranformer activates against an node of the tree
            If its name, arglist and types match (where any of them could be wildcards), it is "active"
                any scopal args it has with criteria are passed to that node of the tree and marked as required
                that next node must match or it fails
            If it fails, the transformer runs against the tree from the place right after where it activated
        The node where the tranformer was activated gets replaced *entirely* by the replacement node
        To match a conjunction it needs to be called out specifically as a conjunction