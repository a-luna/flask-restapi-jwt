.PHONY: install upgrade test test-cov run all

install:
	@echo 'INSTALLING REQUIRED PYTHON PACKAGES...'
	@output=`pip install --upgrade pip setuptools wheel 2>&1` || echo $output
	@output=`pip install -r requirements.txt 2>&1` || echo $output

upgrade:
	@echo 'UPGRADING INSTALLED PYTHON PACKAGES...'
	@pip-review -av

test:
	@echo 'RUNNING UNIT TESTS...'
	@flask test

test-cov:
	@echo 'RUNNING UNIT TESTS AND GENERATING CODE COVERAGE...'
	@flask cov

run:
	@echo 'STARTING FLASK WEB APPLICATION...'
	@flask run -p 5001

all: install test-cov run
