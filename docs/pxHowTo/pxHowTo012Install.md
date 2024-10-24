## Installing Perplexity
Perplexity is all Python code, with one exception: it requires the DELPH-IN [ACE parser](http://sweaglesw.org/linguistics/ace/) for using the DELPH-IN grammars that parse natural language. 

Below are instructions for installing everything you'll need to run Perplexity and begin developing applications.

### Clone Perplexity Using GitHub LFS
> VERY IMPORTANT: This project uses [GitHub LFS](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-git-large-file-storage) for storing grammar files. You won't be able to use it properly unless you install [GitHub LFS](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-git-large-file-storage) and activate it for the repository by following the below steps.

1. The Perplexity repository contains very large grammar files and it uses [GitHub LFS](https://git-lfs.com/) to store them. If you don't have GitHub LFS installed yet:
   - Install [GitHub LFS](https://git-lfs.com/) following the instructions at that link
   - `git lfs install` for the git user account that you will clone Perplexity with
2. `cd` to the directory where you want to clone Perplexity
3. (must be done after the above steps!) Clone the Perplexity project: 
   - `git clone https://github.com/EricZinda/Perplexity.git`

Now you can choose to run Perplexity in a Docker container or on your local machine. Instructions for each are below.

### Option 1: Run Perplexity via Docker
> VERY IMPORTANT: This project uses [GitHub LFS](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-git-large-file-storage) for storing large grammar files. You won't be able to use it properly unless you install [GitHub LFS](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-git-large-file-storage), activate it for your account, and *then* clone the repository as described above.

0. Clone Perplexity using GitHub LFS as described above
2. [Install Docker](https://docs.docker.com/engine/install/)
2. Follow the instructions at the top of the [docker/Dockerfile](https://github.com/EricZinda/Perplexity/blob/main/docker/Dockerfile) file in the Perplexity repository to build an image and run a sample

### Option 2: Run Perplexity on Your Machine
> VERY IMPORTANT: This project uses [GitHub LFS](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-git-large-file-storage) for storing large grammar files. You won't be able to use it properly unless you install [GitHub LFS](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-git-large-file-storage), activate it for your account, and *then* clone the repository as described above.

0. Clone Perplexity using GitHub LFS as described above
1. [Install Python 3.8](https://www.python.org/downloads/) or greater on your machine
2. `cd` to the directory where you cloned Perplexity: 
   - `cd <Perplexity repository root>`
2. Create an environment for this project: 
   - `python3 -m venv ./env`
3. Activate the environment
   - `source env/bin/activate`
2. Install the libraries required by Perplexity:
   - `pip install pydelphin`
   - `pip install inflect`
   - `pip install openai` (note that the ESL sample is the only thing that uses openai for an example, it will just disable this feature if you don't set an OpenAI key to enable it)

Now you need to install the ACE Parser, which is the only non-Python part of the project:


1. [Install the DELPH-IN ACE parser](http://sweaglesw.org/linguistics/ace/)
2. Make sure your operating system path is set to the ACE binary you download from there. 

> The mac download in the ACE link above *does not* support the Mac M1 processor. You'll need a special build that is only available on the forum at the moment if you have an M1. Download that [here](https://delphinqa.ling.washington.edu/t/compiling-ace-on-macos/486/26).

Notes: 
- The best location for the ACE binary on a Mac is: `/usr/local/bin`, but it can be anywhere as long as the path points to it
- Read the notes in the "Troubleshooting" section of the ACE documentation in the link above: ACE needs execute permissions to your TEMP directory


## Running Tests/Samples on Your Machine
If everything is installed correctly, you should be able to successfully run all the tests:

1. Go to the directory where Perplexity was cloned:
   - `cd <Perplexity repository path>`
2. Activate the environment
   - `source env/bin/activate`
3. Tell Python that it should look in this directory for modules:
   - `export PYTHONPATH=$PYTHONPATH:<Perplexity repository path>`
4. Run the file system example and its tests:
   - `python3 ./file_system_example/examples.py`
   - `/runfolder file_system_example`
5. OR: Run the ESL Restaurant example and its tests:
   - `python3 ./esl/tutorial.py`
   - `/runfolder esl`

## Daily Workflow
Once everything in installed, to begin a session of Perplexity development you need to activate the Python environment you created above and then run Perplexity:

1. Go to the directory where Perplexity was cloned:
   - `cd <Perplexity repository path>`
2. Activate the environment
   - `source env/bin/activate`
3. Tell Python that it should look in this directory for modules:
   - `export PYTHONPATH=$PYTHONPATH:<Perplexity repository path>`
4. Start the Perplexity engine:
   - `python3 ./file_system_example/examples.py` 

## Next Step: Hello World
Now that you've got Perplexity installed, the next step is to [create the minimal "Hello World" application](pxHowTo014HelloWorld.md).

## Compile a Grammar
On the (very rare) chance you will need to compile an ERG grammar, here are the steps:

1. Decide which version you want, in this case we'll use 2020.  Replace 2020 below with the version you select
2. svn checkout http://svn.delph-in.net/erg/tags/2020
   2a. To get the latest (but no commitment on quality) grammar: http://svn.delph-in.net/erg/trunk
3. cd 2020/ace
4. ace -G grammar.dat -g ./config.tdl
5. The grammar file will be called 'grammar.dat' in the 2020/ace folder

