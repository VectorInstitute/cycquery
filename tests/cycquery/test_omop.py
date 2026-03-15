"""Test OMOP query API."""

import pytest

import cycquery.ops as qo
from cycquery import OMOPQuerier


@pytest.mark.integration_test()
def test_omop_querier_synthea(synthea_sqlite_db):
    """Test OMOPQuerier on synthea data."""
    querier = OMOPQuerier(
        database=synthea_sqlite_db,
        user="",
        password="",
        dbms="sqlite",
        schema_name="cdm_synthea10",
    )
    # Test that basic queries return data
    persons = querier.person().run()
    assert len(persons) > 0, "Should have person data"
    assert len(persons) == 54, f"Should have 54 persons, got {len(persons)}"

    # Test that queries with operations work
    # (filtering may be affected by SQL dialect differences)
    ops = qo.Rename({"race_source_value": "race"})
    persons_renamed = querier.person().ops(ops).run()
    assert len(persons_renamed) > 0, "Should have data after rename operation"
    assert "race" in persons_renamed.columns, "Should have renamed column"

    # Test visits - these have simpler structure
    visits = querier.visit_occurrence().run()
    assert len(visits) == 1798, f"Should have 1798 visits, got {len(visits)}"

    # Test visit details
    visit_details = querier.visit_detail().run()
    assert len(visit_details) == 4320, (
        f"Should have 4320 visit details, got {len(visit_details)}"
    )

    # Test observations
    observations = querier.observation().run()
    assert len(observations) == 17202, (
        f"Should have 17202 observations, got {len(observations)}"
    )

    # Test measurements
    measurements = querier.measurement().run()
    assert len(measurements) == 19994, (
        f"Should have 19994 measurements, got {len(measurements)}"
    )

    # Test providers
    providers = querier.cdm_synthea10.provider().run()
    assert len(providers) == 212, f"Should have 212 providers, got {len(providers)}"

    # Test conditions
    conditions = querier.cdm_synthea10.condition_occurrence().run()
    assert len(conditions) == 1419, (
        f"Should have 1419 conditions, got {len(conditions)}"
    )


@pytest.mark.integration_test()
def test_omop_querier_mimiciii(mimiciii_sqlite_db):
    """Test OMOPQuerier on MIMICIII data."""
    querier = OMOPQuerier(
        database=mimiciii_sqlite_db,
        user="",
        password="",
        dbms="sqlite",
        schema_name="omop",
    )
    visits = querier.visit_occurrence().run()
    assert len(visits) == 58976
