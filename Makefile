.PHONY: python-packages install test test-cov run all

python-packages:
	@echo 'INSTALLING REQUIRED PYTHON PACKAGES...'
	@output=`pip install --upgrade pip setuptools wheel 2>&1` || echo $output
	@output=`pip install -r requirements.txt 2>&1` || echo $output

install: python-packages

test:
	@echo 'RUNNING UNIT TESTS...'
	@flask test

test-cov:
	@echo 'RUNNING UNIT TESTS AND GENERATING CODE COVERAGE...'
	@flask cov

run:
	@echo 'STARTING FLASK WEB APPLICATION...'
	@flask run -p 5001

all: clean install test-cov run
