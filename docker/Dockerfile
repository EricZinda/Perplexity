# Before doing any of this you'll need to install Docker
# To publish it, you'll need to get a DockerHub account
#
# To build an image:
# First, build the DockerBaseFile image.  Look in that file for instructions

# Then, from the repository root, run:
#   docker build --no-cache -t p8y -f ./docker/Dockerfile ./
#
# To run the image as a local web server (without using the cloud for storage):
#   docker run --env PYTHONPATH='/' --env DONTUSECLOUD=1 -p 8000:8000 -i p8y:latest
#
# Then you can test using the web browser like this:
#   http://127.0.0.1:8000/?From=user&Body=hello
#
# Or run the tests like this:
# docker run --name testrun2 --env DONTUSEGOOGLE_APPLICATION_CREDENTIALS='' --env PYTHONPATH='/' -i p8y:latest /usr/src/Python-3.8.0/python /esl/tutorial.py "/runfolder errors,howto"
#
# To push your image to docker hub so others can access it:
# 1. Tag it with <your docker username>/<what you want to call it>, for example: inductorsoftware/p8y
#   docker tag p8y:latest inductorsoftware/p8y
#
# 2. Push it to docker hub:
#   docker push inductorsoftware/p8y
#
# 3. Others can then access it by going to: https://hub.docker.com/r/inductorsoftware/p8y
#       i.e. the URL is https://hub.docker.com/r/<your docker hub user name>/<what you called it>
#
# 4. Others can then run your project using the instructions above for running an image
#
# Pushing to AWS:
#   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 864551525312.dkr.ecr.us-east-1.amazonaws.com
#   docker tag p8y:latest 864551525312.dkr.ecr.us-east-1.amazonaws.com/p8y:v20
#   docker push 864551525312.dkr.ecr.us-east-1.amazonaws.com/p8y:v20
#
# Run a shell on an image
#   docker run -it imagename /bin/bash
#
# Get a new shell on a running container:
#   docker container exec -it containername /bin/bash
FROM inductorsoftware/p8ybase:latest

# Install OpenAI for experimental predications
RUN /usr/src/Python-3.8.0/python -m pip install openai

# Set up gunicorn
COPY ./hosting/* /
RUN chmod uog+x /gunicorndocker

# Copy the source for Perplexity
RUN mkdir /data
WORKDIR /
COPY ./perplexity/ /perplexity/
COPY ./file_system_example/ /file_system_example/
COPY ./esl/ /esl/
COPY ./error_test/ /error_test/
COPY ./hello_world/ /hello_world/
COPY ./internals_examples/ /internals_examples/

EXPOSE 8000
CMD ["/gunicorndocker"]
