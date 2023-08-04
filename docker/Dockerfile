# To build an image:
# From the repository root run:
#   docker build --no-cache -t p8y -f ./docker/Dockerfile ./
#
# To run the image and start the esl app:
#   docker run --name something --env PYTHONPATH='/' -i p8y:latest /usr/src/Python-3.8.0/python /esl/tutorial.py
# you'll need to replace "something" with a unique image name

FROM ubuntu
WORKDIR ./
ENV DEBIAN_FRONTEND noninteractive

RUN apt clean && apt -y update && apt -y upgrade
# RUN apt -y update
RUN apt-get -y install wget build-essential checkinstall
RUN apt-get -y install libreadline-dev libncursesw5-dev libssl-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev libffi-dev zlib1g-dev

# Download and build Python
WORKDIR /usr/src
RUN wget https://www.python.org/ftp/python/3.8.0/Python-3.8.0.tgz
RUN tar xzf Python-3.8.0.tgz
WORKDIR /usr/src/Python-3.8.0
RUN ./configure --enable-optimizations
RUN make altinstall

# Install all the tools we'll need later
RUN apt-get update
RUN apt-get -y install git
RUN apt-get -y install nano
RUN apt-get -y install strace
RUN apt-get -y install locales

# Install all the required python libraries
RUN /usr/src/Python-3.8.0/python -m ensurepip
RUN /usr/src/Python-3.8.0/python -m pip install --upgrade pip
RUN /usr/src/Python-3.8.0/python -m pip install pydelphin
RUN /usr/src/Python-3.8.0/python -m pip install inflect

# Make sure we are running as english UTF-8 so the ACE Parser
# can build new grammar images if we ask it to
RUN locale-gen en_US.UTF-8
ENV LANG C.UTF-8

# Get the ERG ACE parser
WORKDIR /usr/src
RUN wget http://sweaglesw.org/linguistics/ace/download/ace-0.9.31-x86-64.tar.gz
RUN tar xzf ace-0.9.31-x86-64.tar.gz
RUN cp ./ace-0.9.31/ace /usr/bin
RUN chmod uog+x /usr/bin/ace

# Make a temp dir with execute permissions for ACE
WORKDIR /usr/src
RUN mkdir mytempdir
RUN chmod uog+x /usr/src/mytempdir
ENV TMPDIR='/usr/src/mytempdir'
# Used by tests to group results of runs on different machines
ENV MACHINE_NAME=docker

# Copy the source for Perplexity
RUN mkdir /data
WORKDIR /
COPY ./perplexity/ /perplexity/
COPY ./file_system_example/ /file_system_example/
COPY ./esl/ /esl/

