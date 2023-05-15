{% raw %}## Installing Perplexity
Perplexity is almost 100% Python code, but it does require the DELPH-IN ACE parser to be able to use the DELPH-IN grammars for parsing natural language. 

Below are instructions for installing everything you'll need to run it and begin developing applications.

### Install Perplexity and Python Libraries
1. `cd` to the directory where you want to install Perplexity
2. Clone the Perplexity project: 
   - `git clone https://github.com/EricZinda/Perplexity.git`
3. `cd` to the directory where you installed Perplexity: 
   - `cd <Perplexity project path>`
4. Install Python 3.8 or greater
5. Create an environment for this project: 
   - `python3 -m venv ./env`
6. Activate the environment
   - `source env/bin/activate`
7. Install the libraries required by Perplexity:
   - `pip install pydelphin`

### Install the ACE Parser

Install the Delphin `ACE` parser from: [http://sweaglesw.org/linguistics/ace/](http://sweaglesw.org/linguistics/ace/) and make sure your path is set to it. 
- Best location for the ACE binary on a Mac is: `/usr/local/bin`
- Note the notes in the "Troubleshooting" section of the ACE documentation in the link above: ACE needs execute permissions to your TEMP directory

## Running Tests
If everything is installed correctly, you should be able to successfully run all the tests:

- Go to the directory where Perplexity was cloned:
  - `cd <Perplexity project path>`
- Tell Python that it should look in this directory for modules:
  - `export PYTHONPATH=$PATH:<Perplexity project path>`
- Start the Perplexity engine:
  - `python3 ./file_system_example/examples.py` 
- Run all the Perplexity tests in the `tests` folder:
  - `/runfolder`

## Daily Workflow
Once everything in installed, to begin a session of Perplexity development you simply need to activate the Python environment you created above and run Perplexity:

- `cd <Perplexity project path>`
- `export PYTHONPATH=$PATH:<Perplexity project path>`
- `python3 ./file_system_example/examples.py` 

## Next Step: Hello World
Now that you've got Perplexity installed, the next step is to [create the minimal "Hello World" application](https://blog.inductorsoftware.com/Perplexity/home/pxHowTo/pxHowTo14HelloWorld).

Last update: 2023-05-15 by EricZinda [[edit](https://github.com/EricZinda/Perplexity/edit/main/docs/pxHowTo/pxHowTo12Install.md)]{% endraw %}