
Interesting facts
    Every row has at least 1 element for every gear
    Every variable is >= 1 (no negatives, no zero)
    everything can be expressed as between(0, N) where N might be infinity
    Need to handle total for each AND total *per previous item* for each

Each gear 
Each gear is a constraint
Each tooth is a value

Between x, y

Do exactly 2, exactly 2

Find all combinations from a list of between n and m elements
Brute force:
    As rows stream in, discard those that can't possibly meet the criteria since on their own they are excluded
    Figure out what the minimum and maximum number of rows can be
    Find all combinations in that range
    Manually check each to see if it matches

Iterative:
    all_nonempty_subsets_stream(var, min, max)
        where instead of counting rows we count values of var
        As we go we also count the other vars and discard those that are out of range

Algorithm:
Start with a set of undetermined solutions
For a given predication do both of these:
    by var value:
        all_nonempty_subsets_var_stream()
    across all:
        all_nonempty_subsets_var_stream()

As rows stream in, discard those that can't possibly meet the criteria since on their own they are excluded
