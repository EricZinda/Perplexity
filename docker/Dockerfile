# Before doing any of this you'll need to install Docker
# To publish it, you'll need to get a DockerHub account
#
# To build an image:
# First, build the DockerBaseFile image.  Look in that file for instructions

# Then, from the repository root, run:
#   docker build --no-cache -t p8y -f ./docker/Dockerfile ./
#
# To run the image and start the esl app (you'll need to replace "something" with a unique image name):
#   docker run --name something --env PYTHONPATH='/' -i p8y:latest /usr/src/Python-3.8.0/python /esl/tutorial.py
#
# To run the image and start the file system app (you'll need to replace "something" with a unique image name):
#   docker run --name something --env PYTHONPATH='/' -i p8y:latest /usr/src/Python-3.8.0/python /file_system_example/examples.py

# To push your image to docker hub so others can access it:
# 1. Tag it with <your docker username>/<what you want to call it>, for example: inductorsoftware/p8y
#   docker tag p8y:latest inductorsoftware/p8y
#
# 2. Push it to docker hub:
#   docker push inductorsoftware/p8y
#   docker push p8y
#
# 3. Others can then access it by going to: https://hub.docker.com/r/inductorsoftware/p8y
#       i.e. the URL is https://hub.docker.com/r/<your docker hub user name>/<what you called it>
#
# 4. Others can then run your project using the instructions above for running an image

FROM p8ybase

# Copy the source for Perplexity
RUN mkdir /data
WORKDIR /
COPY ./perplexity/ /perplexity/
COPY ./file_system_example/ /file_system_example/
COPY ./esl/ /esl/

