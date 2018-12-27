import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.pardir))
from sfo_utils.utils import Util
util = Util()
util.ensure_dir('/var/log/sfo/')


