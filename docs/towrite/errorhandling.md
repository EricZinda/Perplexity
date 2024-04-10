
Start with an MRS

formNotUnderstood means "N/A" or "not implemented" or "don't understand" as opposed to False or True
    For each interpretation (i.e. choice of particular predication implementations or disjunction options)
        There is an error hierarchy (from lowest to highest):
        - Phase 1: Errors that happen trying to generate a single solution 
            - formNotUnderstood can be reported when running a phase 1 predication interpretation to indicate "don't understand"
            - (could be forced or unforced)
            - Could be before or after a disjunction?
        - Phase 2: Errors that happen trying to meet global criteria for a solution group
        - Phase 2: Errors that happen in the system trying to find an implementation that accepts the properties of the phrase and records "formNotUnderstood" if not found
            - We should be treating solution group handlers like "interpretations" for a solution group
        - Phase 2: Errors that happen in code when running a solution group handler
            - N solution group handlers could be run for a given solution group, but ONLY if they return formNotUnderstood. Any other error will assume the answer is a failure and stop.
            - If a solution group generates an error in the handler, this should be thought of as the failure for that group

If we get a successful solution group, the error context is cleared (because it was successful)?
