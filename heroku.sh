#!/bin/bash
flask db upgrade
make install
make upgrade
gunicorn run:app --daemon