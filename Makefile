DOCKER=sudo docker
DOCKERBUILD=$(DOCKER) build
DOCKERRUN=$(DOCKER) run
IMAGETAG=kokomi-discord-bot

program: run

build:
	$(DOCKERBUILD) -t $(IMAGETAG) .

run: build
	$(DOCKERRUN) $(IMAGETAG)

unittest: build
	$(DOCKERRUN) $(IMAGETAG) python -m unittest discover -s ../test
