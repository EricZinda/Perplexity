# Overview
If you are trying to use natural language as an interface to software, the DELPH-IN ecosystem provides a chain of tools that can help. This tool chain can take phrases from [many different languages](NorsourceTop) and convert them into a format called MRS which is designed to be processed by software with high fidelity to the speaker's meaning.

This tutorial walks through the steps required to build a natural language interface to software using DELPH-IN by building an interface to a computer's file system as an example, but the concepts apply to any type of system. When finished, you should understand how to evaluate natural language using MRS with a surprisingly small amount of code. The bulk of the code in a final system will be in implementing the terms used in your domain.

We will use the [English Resource Grammar (ERG)](ErgTop) from DELPH-IN to parse English, but the concepts are the same no matter [which DELPH-IN grammar](NorsourceTop) you use.  In fact, the library functions we build have no dependency on the grammar at all and can be used for any of the DELPH-IN grammars.

Python was chosen as a simple, popular, open-source language available on many platforms. However, the examples and approach shown here could be implemented in any language. There is not much code in the core solver and associated helper functions that would need to be translated. The overwhelming majority of code will be in the implementation of the terms you implement for your own domain.

The tutorial was designed to be read in order, but the most important background for all of the sections is in the first two sections, [The Minimal Recursion Semantics (MRS) Format](devhowtoMRS) and [Building Well-Formed MRS Trees](devhowtoWellFormedTree), which should be read in order. 