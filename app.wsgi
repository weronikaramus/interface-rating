#!/usr/bin/python3.12

import sys
import logging

logging.basicConfig(stream=sys.stderr)

sys.path.insert(0, '/home/epi/21_ramus/projekt-dyplomowy/')

from app import app as application