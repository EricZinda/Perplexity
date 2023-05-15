{% raw %}## Installing Perplexity

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

Install the Delphin `ACE` parser: http://sweaglesw.org/linguistics/ace/ and make sure you have a path to it. 
- best location is /usr/local/bin
- Note the notes in the "Troubleshooting" section of the parser.  
- ACE needs execute permissions to your TEMP directory

## Running Tests
If everything is installed correctly, you should be able to successfully run all the tests:

- cd <Perplexity project path>
- export PYTHONPATH=$PATH:<Perplexity project path>
- python3 ./file_system_example/examples.py 

## Docs
If you want to build the docs:
- pip install marko

Other instructions TBW.

Last update: 2023-05-15 by EricZinda [[edit](https://github.com/EricZinda/Perplexity/edit/main/docs/pxHowTo/pxHowTo12Install.md)]{% endraw %}