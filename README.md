# Kokomi Discord Bot
General purpose Discord bot. Written in Python to gain access to many packages, and in OOP paradigm to allow easy implementation of new features, Kokomi strives to be the bot of choice for small Discord servers. 

**DISCLAIMER:** Performance on a big server (or more than one server) has not been tested (nor is it this bot's intended use case), therefore, by doing so you do it at your own risk. 

## Features
- Music playback from popular websites.
- Reactions using still and animated images from popular sources.

## How to use
Kokomi can be run in two different ways. No matter which one is chosen, a set of environmental variables must be provided for the bot to function properly (such as a Discord bot's token, or tokens to external APIs). The recommended way of achieving this is to provide a ```.env``` file with required variables in the project's root directory. The list of required variables can be found in ```src/config.py```.

### Recommended way: using Docker
Simply building a Docker image using ```Dockerfile``` and running a container should be enough to get Kokomi up and running.

### Alternative way: running the Python script
Kokomi can also be run by launching the ```app.py``` script in ```src``` directory. You must have a working ffmpeg and imagemagick installation, as well as Python requirements specified in ```requirements.txt```.

## Hosting
Since Kokomi can be used with Docker, hosting is not a problem, as long as appropriate environmental variables are set. ```heroku.yaml``` file is provided if your desired hosting service is Heroku.
