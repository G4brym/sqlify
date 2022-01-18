#!/usr/bin/env bash

set -e
set -x

pytest --cov=sqlify/ --cov-fail-under=50
coverage report --show-missing
