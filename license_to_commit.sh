#/bin/bash
pytest pyosmo/tests/
pylint *
flake8 --max-line-length 120 --ignore=E722,F401,E402