.PHONY: clean, dist, install


install:
	poetry install

clean:
	rm -rf dist
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

dist:
	poetry buiuld
	ls -l dist
