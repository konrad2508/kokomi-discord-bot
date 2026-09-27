DOCKER=sudo docker
DOCKERBUILD=$(DOCKER) build
DOCKERRUN=$(DOCKER) run --env-file .env
IMAGETAG=kokomi-discord-bot

program: run

build:
	$(DOCKERBUILD) -t $(IMAGETAG) .

run: build
	$(DOCKERRUN) $(IMAGETAG)

unittest: build
	$(DOCKERRUN) $(IMAGETAG) uv run -m unittest discover -s test
