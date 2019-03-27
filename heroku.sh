#!/bin/bash
flask db upgrade
gunicorn run:app --daemon