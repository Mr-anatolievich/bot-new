structure:
	python generate_structure.py

readme:
	python generate_readme.py

docs:
	pydoc-markdown

changelog:
	npx conventional-changelog -p angular -i CHANGELOG.md -s

all: structure readme docs changelog
