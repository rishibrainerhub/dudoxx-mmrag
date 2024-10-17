# Determine the operating system
OS := $(shell uname)

# Use different commands based on the operating system
ifeq ($(OS), Linux)
    # Commands for Linux (Ubuntu)
    DC := docker-compose
    PS := sudo docker ps
    BUILD := sudo $(DC) -f docker-compose.yml build
    UP := sudo $(DC) -f docker-compose.yml up
    DOWN := sudo $(DC) -f docker-compose.yml down
	
else ifeq ($(OS), Windows_NT)
    # Commands for Windows
    DC := docker compose
    PS := docker ps
    BUILD := $(DC) -f docker-compose.yml build
    UP := $(DC) -f docker-compose.yml up
    DOWN := $(DC)-f docker-compose.yml down
else
    $(error Unsupported operating system)
endif

# Define targets
ps:
	$(PS)

build:
	$(BUILD)

up:
	$(UP)

down d:
	$(DOWN)

run r: build up

test t: test-build test-up