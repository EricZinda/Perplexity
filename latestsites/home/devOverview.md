{% raw %}# Overview
The DELPH-IN Consortium has developed a large and rich set of technologies for manipulating natural language. The list of [DELPH-IN applications](https://blog.inductorsoftware.com/docsproto/home/DelphinApplications/) is a great place to start for a survey of different approaches to using them.  There you will find pointers to uses such as identification of speculative or negated event mentions in biomedical text (MacKinlay et al 2011), question generation (Yao et al 2012), detecting the scope of negation (Packard et al 2014), relating natural language to robot control language (Packard 2014), and recognizing textual entailment (PETE task; Lien & Kouylekov 2015). ERS representations have also been beneficial in semantic transfer-based MT (Oepen et al 2007, Bond et al 2011), ontology acquisition (Herbelot & Copestake 2006), extraction of glossary sentences (Reiplinger et al 2012), sentiment analysis (Kramer & Gordon 2014), and the ACL Anthology Searchbench (Schäfer et al 2011), and many more.

This tutorial is designed to show *developers* how to consume a narrow set of DELPH-IN technologies (especially MRS and [ACE](http://sweaglesw.org/linguistics/ace/)) to build an application. It focuses on *one particular* application (a natural language interface to a computer's file system), but the concepts should apply to any type of constrained system ('constrained' in the sense of the size of the world under discussion). It also takes *one particular approach* to building the system by logically evaluating the output of the DELPH-IN parsers against a world definition. While this approach may not be the right one for every application, the concepts illustrated and the tools used along the way should be more broadly applicable.

The tutorial will use the [DELPH-IN English Resource Grammar (ERG)](https://blog.inductorsoftware.com/docsproto/erg/ErgTop/) to parse English, but the concepts are the same across the [DELPH-IN grammars](https://blog.inductorsoftware.com/docsproto/grammars/NorsourceTop/).  In fact, the library functions we build have no dependency on the grammar at all. They can be used for any of the DELPH-IN grammars.

Python was chosen as a simple, popular, open-source language available on many platforms. However, the examples and approach shown here could be implemented in any language. There is not much code in the core solver and associated helper functions that would need to be translated. The overwhelming majority of code will be in the implementation of the terms you implement for your own domain.

It is designed to be read in order, but the most important background is in the first two sections, The Minimal Recursion Semantics (MRS) Format and Building Well-Formed MRS Trees. These should definitely be read before moving on to the rest of the topics. The rest of the topics broadly break down into *conceptual topics* which cover the algorithms and concepts needed to implement a system and *how-to topics* which walk through writing the Python code to implement them.

> Comprehensive source for the completed tutorial is available [here](https://github.com/EricZinda/Perplexity).


Last update: 2023-05-14 by EricZinda [[edit](https://github.com/EricZinda/Perplexity/edit/main/docs/devOverview.md)]{% endraw %}