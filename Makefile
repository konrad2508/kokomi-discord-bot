DOCKER=sudo docker
DOCKERBUILD=$(DOCKER) build
ENVFILE=$(if $(wildcard .env),--env-file .env,)
DOCKERRUN=$(DOCKER) run $(ENVFILE)
IMAGETAG=kokomi-discord-bot

program: run

build:
	$(DOCKERBUILD) -t $(IMAGETAG) .

run: build
	$(DOCKERRUN) $(IMAGETAG)

unittest: build
	$(DOCKERRUN) $(IMAGETAG) uv run -m unittest discover -s test
