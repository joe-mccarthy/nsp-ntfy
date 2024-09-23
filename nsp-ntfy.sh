#!/bin/bash

python -m venv .nsp-ntfy
source .nsp/bin/activate
pip install -r $PWD/requirements.txt
python $PWD/src/application.py -c $1 -nsp $2