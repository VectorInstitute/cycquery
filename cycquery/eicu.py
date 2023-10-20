"""EICU-CRD query module.

Supports querying of eICU.

"""

import logging

from cycquery.base import DatasetQuerier
from cycquery.utils.log import setup_logging


# Logging.
LOGGER = logging.getLogger(__name__)
setup_logging(print_level="INFO", logger=LOGGER)


class EICUQuerier(DatasetQuerier):
    """EICU dataset querier."""
