# Perplexity
This is the fully Python based implementation of the [Perplexity engine](https://perplexitygame.com/).

It has a [tutorial](https://blog.inductorsoftware.com/Perplexity/) that explains how it is built and how it leverages [DELPH-IN](https://delph-in.github.io/docs/) technologies, in great detail.


## Installation via Docker
> VERY IMPORTANT: This project uses [GitHub LFS](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-git-large-file-storage) for storing the grammar files, you won't be able to use it properly unless you install [GitHub LFS](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-git-large-file-storage) and activate it for the repository before following the below steps.

1. Install Docker
2. Follow the instructions at the top of the docker/Dockerfile file to build an image and run a sample

## Installation
> VERY IMPORTANT: This project uses [GitHub LFS](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-git-large-file-storage) for storing the grammar files, you won't be able to use it properly unless you install [GitHub LFS](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-git-large-file-storage) and activate it for the repository before following the below steps.

1. Install ACE
2. Install Python 3.8 or greater
3. Open a command window, from within it:
3. Create an environment:
~~~
   python3 -m venv env
~~~
4. Activate the environment:
~~~
   source env/bin/activate
~~~
5. Install the required libraries:
~~~
   pip install pydelphin 
   pip install inflect
~~~

Then, to run the ESL sample:
1. Type this in the command window, where <path to root> is a fully qualified path to the repository root:
~~~
    PYTHONPATH=<path to root>
    export PYTHONPATH
~~~

To run the ESL sample, from the root of the repository, run this from the same console window:
~~~
   python3 ./esl/tutorial.py
~~~
