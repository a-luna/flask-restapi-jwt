#!/bin/bash
python create_pem.py
gunicorn run:app
