#!/bin/bash
flask db upgrade
make install
make upgrade
make run
gunicorn run:app -w 3 --daemon