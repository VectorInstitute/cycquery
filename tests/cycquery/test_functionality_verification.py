"""Comprehensive functional test to verify core cycquery functionality with SQLite."""

import pytest

import cycquery.ops as qo
from cycquery import OMOPQuerier


@pytest.mark.integration_test()
def test_core_functionality_with_sqlite(synthea_sqlite_db):
    """Verify all core functionality works correctly with SQLite backend."""
    print("\n" + "=" * 70)
    print("COMPREHENSIVE FUNCTIONALITY TEST: SQLite Backend")
    print("=" * 70)

    # Test 1: Basic connection and querying
    print("\n✓ Test 1: Database connection")
    querier = OMOPQuerier(
        database=synthea_sqlite_db,
        user="",
        password="",
        dbms="sqlite",
        schema_name="cdm_synthea10",
    )
    assert querier is not None
    assert querier.db is not None
    print("  SUCCESS: Database connected")

    # Test 2: List schemas and tables
    print("\n✓ Test 2: Schema and table discovery")
    schemas = querier.list_schemas()
    assert len(schemas) >= 4
    print(f"  SUCCESS: Found {len(schemas)} schemas")

    tables = querier.list_tables(schema_name="cdm_synthea10")
    assert len(tables) >= 40
    print(f"  SUCCESS: Found {len(tables)} tables in cdm_synthea10")

    # Test 3: Query person data
    print("\n✓ Test 3: Person data retrieval")
    persons = querier.person().run()
    assert len(persons) == 54
    assert "person_id" in persons.columns
    assert "gender_source_value" in persons.columns
    print(f"  SUCCESS: Retrieved {len(persons)} person records")
    print(f"  Columns: {', '.join(list(persons.columns[:5]))}...")

    # Test 4: Query visits
    print("\n✓ Test 4: Visit data retrieval")
    visits = querier.visit_occurrence().run()
    assert len(visits) == 1798
    assert "visit_occurrence_id" in visits.columns
    print(f"  SUCCESS: Retrieved {len(visits)} visit records")

    # Test 5: Test joins
    print("\n✓ Test 5: Table joins")
    persons_query = querier.person()
    visits_query = querier.visit_occurrence()
    joined = visits_query.join(persons_query, "person_id").run()
    assert len(joined) > 0
    assert "person_id" in joined.columns
    assert "visit_occurrence_id" in joined.columns
    print(f"  SUCCESS: Joined visits and persons -> {len(joined)} records")

    # Test 6: Test operations
    print("\n✓ Test 6: Query operations")

    # Limit
    limited = querier.person().ops(qo.Limit(10)).run()
    assert len(limited) == 10
    print(f"  SUCCESS: Limit(10) -> {len(limited)} records")

    # Rename
    renamed = querier.person().ops(qo.Rename({"person_id": "patient_id"})).run()
    assert "patient_id" in renamed.columns
    assert "person_id" not in renamed.columns
    print("  SUCCESS: Rename 'person_id' -> 'patient_id'")

    # Drop
    dropped = querier.person().ops(qo.Drop(["location_id"])).run()
    assert "location_id" not in dropped.columns
    print("  SUCCESS: Drop 'location_id' column")

    # Order by
    ordered = querier.person().ops(qo.OrderBy("person_id")).run()
    assert len(ordered) == 54
    print("  SUCCESS: OrderBy 'person_id'")

    # Test 7: Test measurements and observations
    print("\n✓ Test 7: Additional table types")
    measurements = querier.measurement().run()
    assert len(measurements) == 19994
    print(f"  SUCCESS: Retrieved {len(measurements)} measurement records")

    observations = querier.observation().run()
    assert len(observations) == 17202
    print(f"  SUCCESS: Retrieved {len(observations)} observation records")

    visit_details = querier.visit_detail().run()
    assert len(visit_details) == 4320
    print(f"  SUCCESS: Retrieved {len(visit_details)} visit detail records")

    # Test 8: Test custom table access
    print("\n✓ Test 8: Direct table access")
    provider_table = querier.cdm_synthea10.provider().run()
    assert len(provider_table) == 212
    print(f"  SUCCESS: Direct access -> {len(provider_table)} provider records")

    conditions = querier.cdm_synthea10.condition_occurrence().run()
    assert len(conditions) == 1419
    print(f"  SUCCESS: Direct access -> {len(conditions)} condition records")

    # Test 9: Test column listing
    print("\n✓ Test 9: Column introspection")
    visit_cols = querier.list_columns("cdm_synthea10", "visit_occurrence")
    assert len(visit_cols) == 17
    assert "visit_occurrence_id" in visit_cols
    print(f"  SUCCESS: Found {len(visit_cols)} columns in visit_occurrence")

    # Summary
    print("\n" + "=" * 70)
    print("ALL COMPREHENSIVE FUNCTIONALITY TESTS PASSED!")
    print("=" * 70)
    print("\nVerified Functionality:")
    print("  ✓ Database connection and initialization")
    print("  ✓ Schema and table discovery")
    print("  ✓ Basic data retrieval (person, visits, measurements, etc.)")
    print("  ✓ Table joins")
    print("  ✓ Query operations (limit, rename, drop, order)")
    print("  ✓ Multiple table types and schemas")
    print("  ✓ Direct table access via querier attributes")
    print("  ✓ Column introspection")
    print(
        f"\nTotal records successfully retrieved and validated: {len(persons) + len(visits) + len(measurements) + len(observations) + len(visit_details)}"
    )
    print("\n✅ SQLite backend is fully functional for cycquery!")
    print("=" * 70)
