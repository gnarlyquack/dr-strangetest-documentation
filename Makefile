.PHONY: build
build:
	python src/build.py dev


.PHONY: release
release:
	python src/build.py release
