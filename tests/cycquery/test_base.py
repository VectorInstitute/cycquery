"""Test base dataset querier, using OMOPQuerier as an example."""

import pytest

from cycquery import OMOPQuerier


@pytest.mark.integration_test()
def test_dataset_querier(synthea_sqlite_db):
    """Test base querier methods using OMOPQuerier."""
    querier = OMOPQuerier(
        database=synthea_sqlite_db,
        user="",
        password="",
        dbms="sqlite",
        schema_name="cdm_synthea10",
    )
    # SQLite may include an extra system table/schema compared to PostgreSQL
    assert len(querier.list_tables()) >= 66
    assert len(querier.list_schemas()) >= 4  # SQLite includes 'main' schema
    assert len(querier.list_tables(schema_name="cdm_synthea10")) >= 43
    visit_occrrence_columns = querier.list_columns("cdm_synthea10", "visit_occurrence")
    assert len(visit_occrrence_columns) == 17
    assert "visit_occurrence_id" in visit_occrrence_columns
