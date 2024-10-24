# Perplexity
> VERY IMPORTANT: This project uses [GitHub LFS](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-git-large-file-storage) for storing its large grammar files. BEFORE CLONING IT, follow the [installation instructions](https://blog.inductorsoftware.com/Perplexity/home/pxHowTo/pxHowTo012Install/) for installing and activating GitHub LFS for your account.

Perplexity is a Python framework for building natural language interfaces to software. It does deep linguistic processing by using the [DELPH-IN](https://delph-in.github.io/docs/home/Home/) technologies which take a very different approach from that used in Large Language Models. To use Perplexity, you implement a set of logic-based functions that represent the words in your domain using Python. Thus, it is truly "hallucination-free" because is it uses only code that you have written, that can be inspected, debugged, etc. There is no "magic" going on. You can always understand exactly why a phrase was understood the way it was because you can debug it using regular tools, applied to regular Python code. The cost for this approach is that you actually need to implement the logic for all the words in your domain.

The magic of this approach is that your users get to interface with your software using actual English (other grammars are available but have not been tested in Perplexity yet).

It has a [tutorial](https://blog.inductorsoftware.com/Perplexity/) that explains how it is built and how it leverages [DELPH-IN](https://delph-in.github.io/docs/) technologies, in great detail.

To install and run the engine and examples, follow the [installation instructions](https://blog.inductorsoftware.com/Perplexity/home/pxHowTo/pxHowTo012Install/).
