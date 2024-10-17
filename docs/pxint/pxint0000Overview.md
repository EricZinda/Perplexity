## Perplexity Internals
This section walks through the details of implementing the concepts described in the [MRS Solver Conceptual](../devcon/devcon0000Overview) section in a Python application.  It is assumed that the concepts from that section are understood (and links are always provided).

This section describes, in detail, how to build a solver like Perplexity. It is simplified, however, from the actual Perplexity code. It is designed to describe the basic architecture for someone who wants to understand the system more deeply without getting lost in the details, or for someone that wants to build a similar system.

If you just want to *use* the Perplexity system to build a natural language interface to a program, you can also just jump right to the ["Using Perplexity"](../pxHowTo/pxHowTo010Overview) section. If you want to understand how it all works, you're in the right place.