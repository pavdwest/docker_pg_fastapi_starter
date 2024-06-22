import sys

import loguru


logger = loguru.logger
logger.remove()
logger.add(sys.stdout, colorize=True)
