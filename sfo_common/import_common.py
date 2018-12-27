#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright © 2007 Free Software Foundation, Inc. <https://fsf.org/>
#
# Licensed under the GNU General Public License, version 3 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    https://jxself.org/translations/gpl-3.zh.shtml
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.pardir))
import re
import copy
import time
import json
import uuid
import socket
import struct
import errno
import random
import atexit
import signal
import psutil
import schedule
import asyncore
import threading
import requests
import datetime
import platform
import multiprocessing
import logging.config
from sfo_common.config_parser import *
from sfo_utils.utils import Util
from threading import Event
from sfo_common.models import *
from sfo_common import db
from sqlalchemy import and_,or_
from sfo_utils import reg_templates
from concurrent.futures import ThreadPoolExecutor
from pykafka import KafkaClient
from swiftclient import client

config = Config()
util = Util()
evt = Event()
logging.config.fileConfig(config.logging_conf)
logger = logging.getLogger("agent")