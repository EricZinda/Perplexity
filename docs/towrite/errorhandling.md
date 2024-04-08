
Start with an MRS
    For each interpretation (i.e. choice of particular predication implementations or disjunction options)
        There is an error hierarchy (from lowest to highest):
        - Phase 1: Errors that happen trying to generate a single solution 
            - (could be forced or unforced)
            - Could be before or after a disjunction?
        - Phase 2: Errors that happen trying to meet global criteria for a solution group
        - Phase 2: Errors that happen in the system trying to find an implementation that accepts the properties of the phrase (and records "formNotUnderstood" if not found)
        - Phase 2: Errors that happen in code when processing a solution group that met its global criteria

If we get a successful solution group, the error context is cleared (because it was successful)
