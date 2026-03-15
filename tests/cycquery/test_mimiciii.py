"""Test MIMICIII query API."""

import pytest

from cycquery import MIMICIIIQuerier


@pytest.mark.integration_test()
def test_mimiciii_querier(mimiciii_sqlite_db):
    """Test MIMICIIIQuerier."""
    querier = MIMICIIIQuerier(
        dbms="sqlite",
        database=mimiciii_sqlite_db,
        user="",
        password="",
    )
    custom_tables = querier.list_custom_tables()
    assert "diagnoses" in custom_tables
    assert "labevents" in custom_tables
    assert "chartevents" in custom_tables

    diagnoses = querier.diagnoses().run(limit=10)
    assert len(diagnoses) == 10
    assert "long_title" in diagnoses

    labevents = querier.labevents().run(limit=10)
    assert len(labevents) == 10
    assert "itemid" in labevents

    chartevents = querier.chartevents().run(limit=10)
    assert len(chartevents) == 10
    assert "itemid" in chartevents
