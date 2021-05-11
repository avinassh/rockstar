clean:
	rm -rf build dist rockstar.egg-info

build: clean
	python3 -m build

test-upload: build
	python3 -m twine upload --repository testpypi dist/*

upload: build
	python3 -m twine upload dist/*
