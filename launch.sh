#!/bin/bash

PATH_TO_VENV=$1
PATH_TO_PS=$2

source $PATH_TO_VENV/bin/activate
cd $PATH_TO_PS

python setup.py install
pserve production.ini

