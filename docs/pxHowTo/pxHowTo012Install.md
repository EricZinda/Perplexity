## Installing Perplexity
Perplexity is almost 100% Python code, but it does require the DELPH-IN [ACE parser](http://sweaglesw.org/linguistics/ace/) for using the DELPH-IN grammars that parse natural language. 

Below are instructions for installing everything you'll need to install Perplexity and begin developing applications.

### Install Perplexity and Python Libraries

0. Perplexity has very large grammar files in its repository and so uses [git LFS](https://git-lfs.com/) to store them. If you don't have git LFS installed yet:
   - Install [git LFS](https://git-lfs.com/) following the instructions at that link
   - `git lfs install` for the git user account that you will clone Perplexity with
1. `cd` to the directory where you want to install Perplexity
2. Clone the Perplexity project: 
   - `git clone https://github.com/EricZinda/Perplexity.git`
3. `cd` to the directory where you installed Perplexity: 
   - `cd <Perplexity repository path>`
1. Install Python 3.8 or greater
2. Create an environment for this project: 
   - `python3 -m venv ./env`
3. Activate the environment
   - `source env/bin/activate`
2. Install the libraries required by Perplexity:
   - `pip install pydelphin`

### Install the ACE Parser

Install the DELPH-IN `ACE` parser from: [http://sweaglesw.org/linguistics/ace/](http://sweaglesw.org/linguistics/ace/) and make sure your path is set to the ACE binary you download from there. 

> The mac download in the ACE link above *does not* support the Mac M1 processor. You'll need a special build that is only available on the forum at the moment if you have an M1. Download that [here](https://delphinqa.ling.washington.edu/t/compiling-ace-on-macos/486/26).
- The best location for the ACE binary on a Mac is: `/usr/local/bin`, but it can be anywhere as long as the path points to it
- Read the notes in the "Troubleshooting" section of the ACE documentation in the link above: ACE needs execute permissions to your TEMP directory


## Running Tests
If everything is installed correctly, you should be able to successfully run all the tests:

1. Go to the directory where Perplexity was cloned:
   - `cd <Perplexity repository path>`
2. Activate the environment
   - `source env/bin/activate`
3. Tell Python that it should look in this directory for modules:
   - `export PYTHONPATH=$PATH:<Perplexity repository path>`
4. Start the Perplexity engine:
   - `python3 ./file_system_example/examples.py` 
5. Run all the Perplexity tests in the `tests` folder:
   - `/runfolder`

## Daily Workflow
Once everything in installed, to begin a session of Perplexity development you need to activate the Python environment you created above and then run Perplexity:

1. Go to the directory where Perplexity was cloned:
   - `cd <Perplexity repository path>`
2. Activate the environment
   - `source env/bin/activate`
3. Tell Python that it should look in this directory for modules:
   - `export PYTHONPATH=$PATH:<Perplexity repository path>`
4. Start the Perplexity engine:
   - `python3 ./file_system_example/examples.py` 

## Next Step: Hello World
Now that you've got Perplexity installed, the next step is to [create the minimal "Hello World" application](pxHowTo014HelloWorld.md).