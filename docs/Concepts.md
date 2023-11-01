## 
Conceptually, any noun predication like `special_n(x)`, when called with unbound `x` should yield:
- the concept `special`
- any other concepts that specialize `special` such as `soup`, `salad`
- any instances of the above concepts

The problem is that, while the instances are a flat list of things that "are a" special, the concepts are a hierarchy. When generating solution sets to form into groups, putting "soup" and "salad" into the same group makes sense, but this group shouldn't include "special" too.  If there are overlapping concepts then we will get duplicate answers?

Basically, every set of concepts that span all the individuals makes sense, and none should overlap

So, if we have the following hierarchy:

1.    special
      |
2.    soup            salad
      |       |       |       |
3.    lentil  tomato  green   beet


Each level of the hierarchy is a disjunction that should be returned in a different solution set.

But: what if there are instances that derive from a non-leaf level of the hierarchy (like "special") directly? then these disjunctions will have different answers

Scenarios:
      "What kinds of cars do you have?"
      "what are the/your specials?"