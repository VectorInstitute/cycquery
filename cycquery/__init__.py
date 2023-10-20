"""The ``query`` API provides classes to query EHR databases."""

try:
    import sqlalchemy
except ImportError:
    raise ImportError(
        "CyclOps is not installed with query API support! Please install using 'pip install cyclops[query]'.",  # noqa: E501
    ) from None


from cycquery.base import DatasetQuerier
from cycquery.eicu import EICUQuerier
from cycquery.gemini import GEMINIQuerier
from cycquery.mimiciii import MIMICIIIQuerier
from cycquery.mimiciv import MIMICIVQuerier
from cycquery.omop import OMOPQuerier
