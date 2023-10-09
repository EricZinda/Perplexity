The basic flow is this:
    - Generate all the solutions for a given set of predication interpretations
        - "Predication interpretation" means one interpretation of a predication given the input.
        - So, if a predication like fw_seq(x, y), returns 2 *alternative* y's for a given x, which should not be in the same solution group, that is two different interpretations
        - Another alternative is "the soup", where it is really be interpreted as a special kind of noun, not using "the" as a determiner
    - Do phase 2 on them
    - Do the next set

Design Alternatives:
    - Start by just assuming that each alternative is a different interpretation
        - For a given MRS, gather all of the alternatives up front before execution
        - Then execute each combination of them
    - Mark predications as mutually exclusive
        - Make "the soup" be a tree transform?