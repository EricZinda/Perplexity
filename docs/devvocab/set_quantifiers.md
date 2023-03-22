Base approach:
Get a rstr set value.  This defines the cardinal group that needs to be checked in collective and distributive mode.
Run it in collective mode: may find several solutions with different rstr values
    Each solution is a cardinal group solution
Run it in dist mode: may only find solutions to some of the items
    Put all of these into a single cardinal group solution

The cardinal:
    collective: checks if the cardinal is true for the rstr values in that collective
    distributive: returns all combinations? that make the cardinal true
        "a few children are eating a pizza"

For standard quantifiers:
Run the cardinal against the resultset:
    The cardinal must be true for each cardinal group, and may have some restriction about how many groups there can be
Run the quantifier against the cardinal resultset and return it
