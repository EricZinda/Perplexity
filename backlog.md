Remaining work to be shown in the tutorial:
  
- Support for prepositions
  - show declaring verbs that understand prepositions

- Sort error messages by returning an error priority from generate_message so that, in phrases like "delete "file2.txt"", we get the error not the "didn't understand X" 
- Get sentence force by looping through variables
- "Temp" is in this folder
  - Has an "Index" which is != the variable that is sentence force
- Theory: We don't need to choose different variations of the index of the phrase based on "comm", "ques", etc
  - Except: if we want to use abductive logic to make "The door is open" not evaluated as a question