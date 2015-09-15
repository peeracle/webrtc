.PHONY: all clean package test tox

all: clean test

clean:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

package:
	python setup.py sdist

test:
	nosetests -v --with-coverage --cover-package=appurify --cover-erase --cover-html --nocapture

tox:
	tox -r
