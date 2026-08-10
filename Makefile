.PHONY: help install test build docker pypi clean

help:
	@echo "BRAVIA Control Center Developer Makefile"
	@echo "----------------------------------------"
	@echo "make install    - Install bravia-control package in editable mode"
	@echo "make run        - Run local web server on port 8888"
	@echo "make build      - Build PyPI source distribution & wheel"
	@echo "make docker     - Build multi-arch Docker image"
	@echo "make pypi       - Upload package to PyPI"
	@echo "make clean      - Clean build artifacts"

install:
	pip install -e .

run:
	python3 -m bravia_control serve --port 8888

build:
	python3 -m pip install --upgrade build
	python3 -m build

docker:
	docker build -t anumac/bravia-control-center:latest .

pypi: build
	python3 -m pip install --upgrade twine
	python3 -m twine upload dist/*

clean:
	rm -rf build/ dist/ *.egg-info bravia_control.egg-info
