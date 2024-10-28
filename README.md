# Perplexity
> VERY IMPORTANT: This project uses [GitHub LFS](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-git-large-file-storage) for storing its large grammar files. BEFORE CLONING IT, follow the [installation instructions](https://blog.inductorsoftware.com/Perplexity/home/pxHowTo/pxHowTo012Install/) for installing and activating GitHub LFS for your account.

Perplexity is a Python framework for building natural language interfaces to software. It does deep linguistic processing by using the [DELPH-IN](https://delph-in.github.io/docs/home/Home/) technologies which take a very different approach from that used in Large Language Models. To use Perplexity, you implement a set of logic-based functions that represent the words in your domain using Python. Thus, it is truly "hallucination-free" because is it uses only code that you have written, that can be inspected, debugged, etc. There is no "magic" going on. You can always understand exactly why a phrase was understood because you can debug it using regular tools, applied to regular Python code. The cost for this approach is that you actually need to implement the logic for all the words in your domain.

The magic of this approach is that your users get to interface with your software using actual English (other grammars are available but have not been tested in Perplexity yet).

It has a [tutorial](https://blog.inductorsoftware.com/Perplexity/) that explains how it is built and how it leverages [DELPH-IN](https://delph-in.github.io/docs/) technologies, in great detail.

To install and run the engine and examples, follow the [installation instructions](https://blog.inductorsoftware.com/Perplexity/home/pxHowTo/pxHowTo012Install/).

## More Details
So far, Perplexity has been tested by implementing 5 games, which have been tried by users over 1000 times at yearly gaming competitions (https://perplexitygame.com), and by implementing a [very simple interactive file system](https://github.com/EricZinda/Perplexity/tree/3b0b65031b7f9396fa940bca0862749fdd1fc699/samples/file_system_example). It is by no means done, but I believe it now represents a good example for showing potential developers what I believe is a novel approach to using DELPH-IN in their applications.

There is documentation designed to teach potential *developers* that are interested in DELPH-IN:
- What [MRS](https://blog.inductorsoftware.com/Perplexity/home/mrscon/devhowto0010MRS/) is and how to construct [well-formed MRS](https://blog.inductorsoftware.com/Perplexity/home/mrscon/devhowto0020WellFormedTree/) 
- Conceptually one way to use DELPH-IN in their applications by [solving MRS as a constraint-satisfaction problem against a well-known state](https://blog.inductorsoftware.com/Perplexity/home/devcon/devcon0000Overview/) which represents the application
- How to [build a simple version of that solver](https://blog.inductorsoftware.com/Perplexity/home/pxint/pxint0000Overview/) using Python if they want to build their own
- How to [use the more robust Perplexity solver](https://blog.inductorsoftware.com/Perplexity/home/pxhowto/pxHowTo010Overview/)  if they want to use one that is already built

The documentation is [all together in one place](https://blog.inductorsoftware.com/Perplexity/home/devOverview/), and the source for Perplexity and all of the samples are [available here on Github]().



Some interesting technical aspects of the solver are:

- It is designed to be a [Python framework](https://blog.inductorsoftware.com/Perplexity/home/pxhowto/pxHowTo010Overview/) that is easy to consume by developers without a formal linguistic training
- It treats solving MRS against a world state as a [constraint satisfaction problem](https://blog.inductorsoftware.com/Perplexity/home/devcon/devcon0010MRSSolver/), which does not require reforming the MRS into any particular logical formalism. This means it is able to handle various approaches to implementing different language constructs, and even mixing approaches
- It can solve a fully-resolved MRS against a known state and [produce all distributive/collective/cumulative solutions](https://blog.inductorsoftware.com/Perplexity/home/devcon/devcon0030MRSSolverSolutionGroups/) 
- It allows for solving MRS interpretations that are less logical and [more (in a linguistics sense) Pragmatic](https://blog.inductorsoftware.com/Perplexity/home/pxhowto/pxHowTo100NonlogicalMeaning/)

A good place to start if you want to use Perplexity is with the [Using Perplexity Tutorial](https://blog.inductorsoftware.com/Perplexity/home/pxhowto/pxHowTo010Overview/).