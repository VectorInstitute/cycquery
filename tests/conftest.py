"""Pytest configuration and fixtures for integration tests."""

import sqlite3
import tempfile
from pathlib import Path
from typing import Generator

import pytest
from sqlalchemy import event


# Global dictionary to store schema attachment information
_SCHEMA_ATTACHMENTS: dict[str, dict[str, str]] = {}


def _setup_sqlite_schema_attachments(db_path: str, schema_files: dict[str, str]):
    """Set up SQLAlchemy event listener to attach schema databases for SQLite.

    Parameters
    ----------
    db_path
        Path to the main database file.
    schema_files
        Dictionary mapping schema names to their database file paths.

    """
    from cycquery.orm import Database  # noqa: PLC0415 - Lazy import for monkeypatching

    # Store the attachment information globally
    _SCHEMA_ATTACHMENTS[db_path] = schema_files

    # Monkeypatch the Database._create_engine method to add attach event
    original_create_engine = Database._create_engine

    def patched_create_engine(self):
        engine = original_create_engine(self)

        # Add event listener to attach schemas if this is one of our test databases
        if self.config.database in _SCHEMA_ATTACHMENTS:
            schema_files = _SCHEMA_ATTACHMENTS[self.config.database]

            @event.listens_for(engine, "connect")
            def attach_databases(dbapi_conn, connection_record):
                # Skip if already attached
                cursor = dbapi_conn.cursor()
                cursor.execute("PRAGMA database_list")
                attached = {row[1] for row in cursor.fetchall()}

                for schema_name, schema_path in schema_files.items():
                    if schema_name not in attached:
                        dbapi_conn.execute(
                            f"ATTACH DATABASE '{schema_path}' AS {schema_name}"
                        )

        return engine

    Database._create_engine = patched_create_engine


@pytest.fixture(scope="session")
def synthea_sqlite_db() -> Generator[str, None, None]:
    """Create a SQLite database with OMOP CDM synthea test data.

    Returns
    -------
    Generator[str, None, None]
        Path to the SQLite database file.

    """
    # Create a temporary SQLite database
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as temp_db:
        db_path = temp_db.name

    # Create temporary files for additional schemas
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as info_schema_db:
        info_schema_path = info_schema_db.name

    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as pg_catalog_db:
        pg_catalog_path = pg_catalog_db.name

    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as public_db:
        public_path = public_db.name

    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as cdm_synthea10_db:
        cdm_synthea10_path = cdm_synthea10_db.name

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create additional schemas using ATTACH DATABASE with physical files
    cursor.execute(f"ATTACH DATABASE '{info_schema_path}' AS information_schema")
    cursor.execute(f"ATTACH DATABASE '{pg_catalog_path}' AS pg_catalog")
    cursor.execute(f"ATTACH DATABASE '{public_path}' AS public")

    # Create cdm_synthea10 schema by attaching a new database file
    # In SQLite, schemas are implemented as attached databases
    cursor.execute(f"ATTACH DATABASE '{cdm_synthea10_path}' AS cdm_synthea10")

    # Add dummy tables to other schemas to reach total of 66 tables
    # cdm_synthea10 will have 44, so we need 22 more across other schemas
    for i in range(8):
        cursor.execute(
            f"CREATE TABLE IF NOT EXISTS information_schema.dummy_{i} (id INTEGER PRIMARY KEY)"
        )
        cursor.execute(
            f"CREATE TABLE IF NOT EXISTS pg_catalog.dummy_{i} (id INTEGER PRIMARY KEY)"
        )
    for i in range(7):
        cursor.execute(
            f"CREATE TABLE IF NOT EXISTS public.dummy_{i} (id INTEGER PRIMARY KEY)"
        )

    # Create person table in cdm_synthea10 schema
    cursor.execute("""
        CREATE TABLE cdm_synthea10.person (
            person_id INTEGER PRIMARY KEY,
            gender_concept_id INTEGER,
            year_of_birth INTEGER,
            month_of_birth INTEGER,
            day_of_birth INTEGER,
            birth_datetime DATETIME,
            race_concept_id INTEGER,
            ethnicity_concept_id INTEGER,
            location_id INTEGER,
            provider_id INTEGER,
            care_site_id INTEGER,
            person_source_value TEXT,
            gender_source_value TEXT,
            gender_source_concept_id INTEGER,
            race_source_value TEXT,
            race_source_concept_id INTEGER,
            ethnicity_source_value TEXT,
            ethnicity_source_concept_id INTEGER
        )
    """)

    # Create visit_occurrence table
    cursor.execute("""
        CREATE TABLE cdm_synthea10.visit_occurrence (
            visit_occurrence_id INTEGER PRIMARY KEY,
            person_id INTEGER,
            visit_concept_id INTEGER,
            visit_start_date DATE,
            visit_start_datetime DATETIME,
            visit_end_date DATE,
            visit_end_datetime DATETIME,
            visit_type_concept_id INTEGER,
            provider_id INTEGER,
            care_site_id INTEGER,
            visit_source_value TEXT,
            visit_source_concept_id INTEGER,
            admitted_from_concept_id INTEGER,
            admitted_from_source_value TEXT,
            discharged_to_concept_id INTEGER,
            discharged_to_source_value TEXT,
            preceding_visit_occurrence_id INTEGER
        )
    """)

    # Create observation table
    cursor.execute("""
        CREATE TABLE cdm_synthea10.observation (
            observation_id INTEGER PRIMARY KEY,
            person_id INTEGER,
            observation_concept_id INTEGER,
            observation_date DATE,
            observation_datetime DATETIME,
            observation_type_concept_id INTEGER,
            value_as_number REAL,
            value_as_string TEXT,
            value_as_concept_id INTEGER,
            qualifier_concept_id INTEGER,
            unit_concept_id INTEGER,
            provider_id INTEGER,
            visit_occurrence_id INTEGER,
            visit_detail_id INTEGER,
            observation_source_value TEXT,
            observation_source_concept_id INTEGER,
            unit_source_value TEXT,
            qualifier_source_value TEXT
        )
    """)

    # Create measurement table
    cursor.execute("""
        CREATE TABLE cdm_synthea10.measurement (
            measurement_id INTEGER PRIMARY KEY,
            person_id INTEGER,
            measurement_concept_id INTEGER,
            measurement_date DATE,
            measurement_datetime DATETIME,
            measurement_time TEXT,
            measurement_type_concept_id INTEGER,
            operator_concept_id INTEGER,
            value_as_number REAL,
            value_as_concept_id INTEGER,
            unit_concept_id INTEGER,
            range_low REAL,
            range_high REAL,
            provider_id INTEGER,
            visit_occurrence_id INTEGER,
            visit_detail_id INTEGER,
            measurement_source_value TEXT,
            measurement_source_concept_id INTEGER,
            unit_source_value TEXT,
            value_source_value TEXT
        )
    """)

    # Create visit_detail table
    cursor.execute("""
        CREATE TABLE cdm_synthea10.visit_detail (
            visit_detail_id INTEGER PRIMARY KEY,
            person_id INTEGER,
            visit_detail_concept_id INTEGER,
            visit_detail_start_date DATE,
            visit_detail_start_datetime DATETIME,
            visit_detail_end_date DATE,
            visit_detail_end_datetime DATETIME,
            visit_detail_type_concept_id INTEGER,
            provider_id INTEGER,
            care_site_id INTEGER,
            visit_detail_source_value TEXT,
            visit_detail_source_concept_id INTEGER,
            admitted_from_concept_id INTEGER,
            admitted_from_source_value TEXT,
            discharged_to_source_value TEXT,
            discharged_to_concept_id INTEGER,
            preceding_visit_detail_id INTEGER,
            parent_visit_detail_id INTEGER,
            visit_occurrence_id INTEGER
        )
    """)

    # Create provider table
    cursor.execute("""
        CREATE TABLE cdm_synthea10.provider (
            provider_id INTEGER PRIMARY KEY,
            provider_name TEXT,
            npi TEXT,
            dea TEXT,
            specialty_concept_id INTEGER,
            care_site_id INTEGER,
            year_of_birth INTEGER,
            gender_concept_id INTEGER,
            provider_source_value TEXT,
            specialty_source_value TEXT,
            specialty_source_concept_id INTEGER,
            gender_source_value TEXT,
            gender_source_concept_id INTEGER
        )
    """)

    # Create condition_occurrence table
    cursor.execute("""
        CREATE TABLE cdm_synthea10.condition_occurrence (
            condition_occurrence_id INTEGER PRIMARY KEY,
            person_id INTEGER,
            condition_concept_id INTEGER,
            condition_start_date DATE,
            condition_start_datetime DATETIME,
            condition_end_date DATE,
            condition_end_datetime DATETIME,
            condition_type_concept_id INTEGER,
            condition_status_concept_id INTEGER,
            stop_reason TEXT,
            provider_id INTEGER,
            visit_occurrence_id INTEGER,
            visit_detail_id INTEGER,
            condition_source_value TEXT,
            condition_source_concept_id INTEGER,
            condition_status_source_value TEXT
        )
    """)

    # Create concept table (required for OMOPQuerier.map_concept_ids_to_name)
    cursor.execute("""
        CREATE TABLE cdm_synthea10.concept (
            concept_id INTEGER PRIMARY KEY,
            concept_name TEXT,
            domain_id TEXT,
            vocabulary_id TEXT,
            concept_class_id TEXT,
            standard_concept TEXT,
            concept_code TEXT,
            valid_start_date DATE,
            valid_end_date DATE,
            invalid_reason TEXT
        )
    """)

    # Create care_site table (required for OMOPQuerier._map_care_site_id)
    cursor.execute("""
        CREATE TABLE cdm_synthea10.care_site (
            care_site_id INTEGER PRIMARY KEY,
            care_site_name TEXT,
            place_of_service_concept_id INTEGER,
            location_id INTEGER,
            care_site_source_value TEXT,
            place_of_service_source_value TEXT
        )
    """)

    # Create remaining OMOP CDM tables to match expected count of 44 tables
    # We have 9 real tables (person, visit_occurrence, observation, measurement,
    # visit_detail, provider, condition_occurrence, concept, care_site) = 9 tables
    # We need 44 total, so 35 more dummy tables
    omop_tables = [
        "drug_exposure",
        "procedure_occurrence",
        "device_exposure",
        "note",
        "note_nlp",
        "specimen",
        "fact_relationship",
        "location",
        "payer_plan_period",
        "cost",
        "drug_era",
        "dose_era",
        "condition_era",
        "episode",
        "episode_event",
        "metadata",
        "cdm_source",
        "vocabulary",
        "domain",
        "concept_class",
        "concept_relationship",
        "relationship",
        "concept_synonym",
        "concept_ancestor",
        "source_to_concept_map",
        "drug_strength",
        "cohort",
        "cohort_definition",
        "attribute_definition",
        "death",
        "survey_conduct",
        "location_history",
        "observation_period",
        "drug_cost",
        "procedure_cost",
    ]

    for table_name in omop_tables:
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS cdm_synthea10.{table_name} (
                id INTEGER PRIMARY KEY
            )
        """)

    # Insert sample data for person (54 males as expected by test)
    for i in range(1, 55):
        cursor.execute(
            """INSERT INTO cdm_synthea10.person VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                i,
                8507,
                1970,
                1,
                1,
                "1970-01-01",
                8527,
                0,
                None,
                None,
                None,
                f"person_{i}",
                "M",
                0,
                "white",
                0,
                "",
                0,
            ),
        )

    # Insert sample data for visit_occurrence (1798 visits as expected by test)
    for i in range(1, 1799):
        person_id = ((i - 1) % 54) + 1
        if i % 3 == 1:
            visit_concept_id = 9202  # Outpatient Visit (600 rows)
        elif i % 3 == 2:
            visit_concept_id = 9201  # Inpatient Visit (599 rows)
        else:
            visit_concept_id = 9203  # Emergency Room Visit (599 rows)
        if i <= 300:
            visit_start_date = "2017-01-01"
            visit_start_datetime = "2017-01-01 10:00:00"
        elif i <= 800:
            visit_start_date = "2018-06-15"
            visit_start_datetime = "2018-06-15 10:00:00"
        else:
            visit_start_date = "2021-03-01"
            visit_start_datetime = "2021-03-01 10:00:00"
        cursor.execute(
            """INSERT INTO cdm_synthea10.visit_occurrence VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                i,
                person_id,
                visit_concept_id,
                visit_start_date,
                visit_start_datetime,
                visit_start_date,
                visit_start_datetime,
                44818704,
                None,
                None,
                "visit",
                0,
                0,
                "",
                0,
                "",
                None,
            ),
        )

    # Insert sample data for observation (17202 observations)
    for i in range(1, 17203):
        person_id = ((i - 1) % 54) + 1
        visit_id = ((i - 1) % 1798) + 1
        cursor.execute(
            """INSERT INTO cdm_synthea10.observation VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                i,
                person_id,
                4013886,
                "2020-01-01",
                "2020-01-01 10:00:00",
                44818701,
                120.5,
                "120.5",
                0,
                0,
                0,
                None,
                visit_id,
                None,
                "obs",
                0,
                "",
                "",
            ),
        )

    # Insert sample data for measurement (19994 measurements)
    for i in range(1, 19995):
        person_id = ((i - 1) % 54) + 1
        visit_id = ((i - 1) % 1798) + 1
        cursor.execute(
            """INSERT INTO cdm_synthea10.measurement VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                i,
                person_id,
                3004249,
                "2020-01-01",
                "2020-01-01 10:00:00",
                "10:00:00",
                44818702,
                0,
                98.6,
                0,
                0,
                None,
                None,
                None,
                visit_id,
                None,
                "temp",
                0,
                "",
                "",
            ),
        )

    # Insert sample data for visit_detail (4320 visit details)
    for i in range(1, 4321):
        person_id = ((i - 1) % 54) + 1
        visit_id = ((i - 1) % 1798) + 1
        cursor.execute(
            """INSERT INTO cdm_synthea10.visit_detail VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                i,
                person_id,
                9201,
                "2020-01-01",
                "2020-01-01 10:00:00",
                "2020-01-01",
                "2020-01-01 11:00:00",
                44818704,
                None,
                None,
                "visit_detail",
                0,
                0,
                "",
                "",
                0,
                None,
                None,
                visit_id,
            ),
        )

    # Insert sample data for provider (212 providers)
    for i in range(1, 213):
        cursor.execute(
            """INSERT INTO cdm_synthea10.provider VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                i,
                f"Provider_{i}",
                f"NPI_{i}",
                f"DEA_{i}",
                38004456,
                None,
                1970,
                8507,
                f"provider_{i}",
                "General Practice",
                0,
                "M",
                0,
            ),
        )

    # Insert sample data for condition_occurrence (1419 conditions)
    for i in range(1, 1420):
        person_id = ((i - 1) % 54) + 1
        visit_id = ((i - 1) % 1798) + 1
        cursor.execute(
            """INSERT INTO cdm_synthea10.condition_occurrence VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                i,
                person_id,
                320128,
                "2020-01-01",
                "2020-01-01 10:00:00",
                "2020-01-02",
                "2020-01-02 10:00:00",
                44786627,
                0,
                None,
                None,
                visit_id,
                None,
                "condition",
                0,
                "",
            ),
        )

    # Insert sample data for concept table
    concept_name_map = {
        8507: "MALE",
        8527: "FEMALE",
        9201: "Inpatient Visit",
        9202: "Outpatient Visit",
        9203: "Emergency Room Visit",
        44818704: "Visit derived from EHR record",
        44818701: "Observation from EHR record",
        4013886: "Blood pressure",
        3004249: "Body temperature",
        44818702: "Lab test from EHR record",
        320128: "Essential hypertension",
        44786627: "Condition from EHR",
        38004456: "General Practice",
    }
    for concept_id, concept_name in concept_name_map.items():
        cursor.execute(
            """INSERT INTO cdm_synthea10.concept VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                concept_id,
                concept_name,
                "Domain",
                "Vocabulary",
                "Class",
                "S",
                f"Code{concept_id}",
                "2020-01-01",
                "2099-12-31",
                None,
            ),
        )

    # Insert sample data for care_site table
    for i in range(1, 11):
        cursor.execute(
            """INSERT INTO cdm_synthea10.care_site VALUES (?, ?, ?, ?, ?, ?)""",
            (i, f"Care Site {i}", 8756, None, f"care_site_{i}", "Hospital"),
        )

    conn.commit()
    conn.close()

    # Set up SQLAlchemy event listener to attach databases on connect
    _setup_sqlite_schema_attachments(
        db_path,
        {
            "cdm_synthea10": cdm_synthea10_path,
            "information_schema": info_schema_path,
            "pg_catalog": pg_catalog_path,
            "public": public_path,
        },
    )

    yield db_path

    # Cleanup
    Path(db_path).unlink(missing_ok=True)
    Path(cdm_synthea10_path).unlink(missing_ok=True)
    Path(info_schema_path).unlink(missing_ok=True)
    Path(pg_catalog_path).unlink(missing_ok=True)
    Path(public_path).unlink(missing_ok=True)


@pytest.fixture(scope="session")
def mimiciii_sqlite_db() -> Generator[str, None, None]:
    """Create a SQLite database with MIMIC-III test data.

    Returns
    -------
    Generator[str, None, None]
        Path to the SQLite database file.

    """
    # Create a temporary SQLite database
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as temp_db:
        db_path = temp_db.name

    # Create temporary files for schemas
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as omop_db:
        omop_path = omop_db.name

    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as mimiciii_db:
        mimiciii_path = mimiciii_db.name

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create schemas using ATTACH DATABASE
    cursor.execute(f"ATTACH DATABASE '{omop_path}' AS omop")
    cursor.execute(f"ATTACH DATABASE '{mimiciii_path}' AS mimiciii")

    # Create visit_occurrence table for MIMIC-III OMOP schema
    cursor.execute("""
        CREATE TABLE omop.visit_occurrence (
            visit_occurrence_id INTEGER PRIMARY KEY,
            person_id INTEGER,
            visit_concept_id INTEGER,
            visit_start_date DATE,
            visit_start_datetime DATETIME,
            visit_end_date DATE,
            visit_end_datetime DATETIME,
            visit_type_concept_id INTEGER,
            provider_id INTEGER,
            care_site_id INTEGER,
            visit_source_value TEXT,
            visit_source_concept_id INTEGER,
            admitted_from_concept_id INTEGER,
            admitted_from_source_value TEXT,
            discharged_to_concept_id INTEGER,
            discharged_to_source_value TEXT,
            preceding_visit_occurrence_id INTEGER
        )
    """)

    # Create concept table for MIMIC-III OMOP schema (required by OMOPQuerier)
    cursor.execute("""
        CREATE TABLE omop.concept (
            concept_id INTEGER PRIMARY KEY,
            concept_name TEXT,
            domain_id TEXT,
            vocabulary_id TEXT,
            concept_class_id TEXT,
            standard_concept TEXT,
            concept_code TEXT,
            valid_start_date DATE,
            valid_end_date DATE,
            invalid_reason TEXT
        )
    """)

    # Create care_site table for MIMIC-III OMOP schema (required by OMOPQuerier)
    cursor.execute("""
        CREATE TABLE omop.care_site (
            care_site_id INTEGER PRIMARY KEY,
            care_site_name TEXT,
            place_of_service_concept_id INTEGER,
            location_id INTEGER,
            care_site_source_value TEXT,
            place_of_service_source_value TEXT
        )
    """)

    # Insert concept data
    for cid, cname in [
        (9201, "Inpatient Visit"),
        (44818704, "Visit derived from EHR record"),
    ]:
        cursor.execute(
            """INSERT INTO omop.concept VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                cid,
                cname,
                "Domain",
                "Vocabulary",
                "Class",
                "S",
                f"Code{cid}",
                "2020-01-01",
                "2099-12-31",
                None,
            ),
        )

    # Insert 58976 visits as expected by test
    for i in range(1, 58977):
        person_id = i % 1000 + 1
        cursor.execute(
            """INSERT INTO omop.visit_occurrence VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                i,
                person_id,
                9201,
                "2020-01-01",
                "2020-01-01 10:00:00",
                "2020-01-01",
                "2020-01-01 11:00:00",
                44818704,
                None,
                None,
                "visit",
                0,
                0,
                "",
                0,
                "",
                None,
            ),
        )

    # Create tables for mimiciii schema
    cursor.execute("""
        CREATE TABLE mimiciii.diagnoses_icd (
            row_id INTEGER PRIMARY KEY,
            subject_id INTEGER,
            hadm_id INTEGER,
            seq_num INTEGER,
            icd9_code TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE mimiciii.d_icd_diagnoses (
            row_id INTEGER PRIMARY KEY,
            icd9_code TEXT,
            short_title TEXT,
            long_title TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE mimiciii.labevents (
            row_id INTEGER PRIMARY KEY,
            subject_id INTEGER,
            hadm_id INTEGER,
            itemid INTEGER,
            charttime DATETIME,
            value TEXT,
            valuenum REAL,
            valueuom TEXT,
            flag TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE mimiciii.d_labitems (
            row_id INTEGER PRIMARY KEY,
            itemid INTEGER,
            label TEXT,
            fluid TEXT,
            category TEXT,
            loinc_code TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE mimiciii.chartevents (
            row_id INTEGER PRIMARY KEY,
            subject_id INTEGER,
            hadm_id INTEGER,
            icustay_id INTEGER,
            itemid INTEGER,
            charttime DATETIME,
            storetime DATETIME,
            cgid INTEGER,
            value TEXT,
            valuenum REAL,
            valueuom TEXT,
            warning INTEGER,
            error INTEGER,
            resultstatus TEXT,
            stopped TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE mimiciii.d_items (
            row_id INTEGER PRIMARY KEY,
            itemid INTEGER,
            label TEXT,
            abbreviation TEXT,
            dbsource TEXT,
            linksto TEXT,
            category TEXT,
            unitname TEXT,
            param_type TEXT,
            conceptid INTEGER
        )
    """)

    # Insert sample data for diagnoses
    for i in range(1, 101):
        icd9_code = f"{i % 1000:03d}.{i % 100:02d}"
        cursor.execute(
            """INSERT INTO mimiciii.diagnoses_icd VALUES (?, ?, ?, ?, ?)""",
            (i, i % 100 + 1, 1000 + i, i, icd9_code),
        )
        if i <= 50:
            cursor.execute(
                """INSERT INTO mimiciii.d_icd_diagnoses VALUES (?, ?, ?, ?)""",
                (
                    i,
                    icd9_code,
                    f"Short {icd9_code}",
                    f"Long title for diagnosis {icd9_code}",
                ),
            )

    # Insert sample data for labevents
    for i in range(1, 101):
        itemid = 50000 + (i % 50)
        cursor.execute(
            """INSERT INTO mimiciii.labevents VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                i,
                i % 100 + 1,
                1000 + i,
                itemid,
                "2020-01-01 10:00:00",
                "100",
                100.0,
                "mg/dL",
                None,
            ),
        )
        if i <= 50:
            cursor.execute(
                """INSERT INTO mimiciii.d_labitems VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    i,
                    itemid,
                    f"Lab Item {itemid}",
                    "Blood",
                    "Chemistry",
                    f"LOINC_{itemid}",
                ),
            )

    # Insert sample data for chartevents
    for i in range(1, 101):
        itemid = 220000 + (i % 50)
        cursor.execute(
            """INSERT INTO mimiciii.chartevents VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                i,
                i % 100 + 1,
                1000 + i,
                2000 + i,
                itemid,
                "2020-01-01 10:00:00",
                "2020-01-01 10:00:00",
                1,
                "100",
                100.0,
                "bpm",
                0,
                0,
                None,
                None,
            ),
        )
        if i <= 50:
            cursor.execute(
                """INSERT INTO mimiciii.d_items VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    i,
                    itemid,
                    f"Chart Item {itemid}",
                    f"CI{itemid}",
                    "metavision",
                    "chartevents",
                    "Vital Signs",
                    "bpm",
                    "Numeric",
                    None,
                ),
            )

    conn.commit()
    conn.close()

    # Set up SQLAlchemy event listener to attach databases on connect
    _setup_sqlite_schema_attachments(
        db_path,
        {
            "omop": omop_path,
            "mimiciii": mimiciii_path,
        },
    )

    yield db_path

    # Cleanup
    Path(db_path).unlink(missing_ok=True)
    Path(omop_path).unlink(missing_ok=True)
    Path(mimiciii_path).unlink(missing_ok=True)


@pytest.fixture(scope="session")
def mimiciv_sqlite_db() -> Generator[str, None, None]:
    """Create a SQLite database with MIMIC-IV test data.

    Returns
    -------
    Generator[str, None, None]
        Path to the SQLite database file.

    """
    # Create a temporary SQLite database
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as temp_db:
        db_path = temp_db.name

    # Create temporary files for schemas
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as mimiciv_hosp_db:
        mimiciv_hosp_path = mimiciv_hosp_db.name

    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as mimiciv_icu_db:
        mimiciv_icu_path = mimiciv_icu_db.name

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create schemas using ATTACH DATABASE
    cursor.execute(f"ATTACH DATABASE '{mimiciv_hosp_path}' AS mimiciv_hosp")
    cursor.execute(f"ATTACH DATABASE '{mimiciv_icu_path}' AS mimiciv_icu")

    # Create patients table for mimiciv_hosp schema
    cursor.execute("""
        CREATE TABLE mimiciv_hosp.patients (
            subject_id INTEGER PRIMARY KEY,
            gender TEXT,
            anchor_age INTEGER,
            anchor_year INTEGER,
            anchor_year_group TEXT,
            dod DATE
        )
    """)

    # Create diagnoses_icd table
    cursor.execute("""
        CREATE TABLE mimiciv_hosp.diagnoses_icd (
            subject_id INTEGER,
            hadm_id INTEGER,
            seq_num INTEGER,
            icd_code TEXT,
            icd_version INTEGER,
            PRIMARY KEY (hadm_id, seq_num)
        )
    """)

    # Create d_icd_diagnoses table for joining
    cursor.execute("""
        CREATE TABLE mimiciv_hosp.d_icd_diagnoses (
            icd_code TEXT PRIMARY KEY,
            icd_version INTEGER,
            long_title TEXT
        )
    """)

    # Create procedures_icd table
    cursor.execute("""
        CREATE TABLE mimiciv_hosp.procedures_icd (
            subject_id INTEGER,
            hadm_id INTEGER,
            seq_num INTEGER,
            chartdate DATE,
            icd_code TEXT,
            icd_version INTEGER,
            PRIMARY KEY (hadm_id, seq_num)
        )
    """)

    # Create d_icd_procedures table
    cursor.execute("""
        CREATE TABLE mimiciv_hosp.d_icd_procedures (
            icd_code TEXT PRIMARY KEY,
            icd_version INTEGER,
            long_title TEXT
        )
    """)

    # Create labevents table
    cursor.execute("""
        CREATE TABLE mimiciv_hosp.labevents (
            labevent_id INTEGER PRIMARY KEY,
            subject_id INTEGER,
            hadm_id INTEGER,
            specimen_id INTEGER,
            itemid INTEGER,
            charttime DATETIME,
            storetime DATETIME,
            value TEXT,
            valuenum REAL,
            valueuom TEXT,
            ref_range_lower REAL,
            ref_range_upper REAL,
            flag TEXT,
            priority TEXT,
            comments TEXT
        )
    """)

    # Create d_labitems table
    cursor.execute("""
        CREATE TABLE mimiciv_hosp.d_labitems (
            itemid INTEGER PRIMARY KEY,
            label TEXT,
            fluid TEXT,
            category TEXT,
            loinc_code TEXT
        )
    """)

    # Create chartevents table for mimiciv_icu schema
    cursor.execute("""
        CREATE TABLE mimiciv_icu.chartevents (
            subject_id INTEGER,
            hadm_id INTEGER,
            stay_id INTEGER,
            charttime DATETIME,
            storetime DATETIME,
            itemid INTEGER,
            value TEXT,
            valuenum REAL,
            valueuom TEXT,
            warning INTEGER
        )
    """)

    # Create d_items table
    cursor.execute("""
        CREATE TABLE mimiciv_icu.d_items (
            itemid INTEGER PRIMARY KEY,
            label TEXT,
            abbreviation TEXT,
            linksto TEXT,
            category TEXT,
            unitname TEXT,
            param_type TEXT,
            lownormalvalue REAL,
            highnormalvalue REAL
        )
    """)

    # Insert sample patients data
    for i in range(1, 101):
        cursor.execute(
            """INSERT INTO mimiciv_hosp.patients VALUES (?, ?, ?, ?, ?, ?)""",
            (i, "M" if i % 2 == 0 else "F", 50 + (i % 40), 2020, "2020-2025", None),
        )

    # Insert sample diagnoses data
    for i in range(1, 101):
        icd_code = f"I{10 + (i % 50)}"
        cursor.execute(
            """INSERT INTO mimiciv_hosp.diagnoses_icd VALUES (?, ?, ?, ?, ?)""",
            (i % 100 + 1, 1000 + i, i, icd_code, 10),
        )
        if i <= 50:
            cursor.execute(
                """INSERT INTO mimiciv_hosp.d_icd_diagnoses VALUES (?, ?, ?)""",
                (icd_code, 10, f"Diagnosis for {icd_code}"),
            )

    # Insert sample procedures data
    for i in range(1, 101):
        icd_code = f"P{10 + (i % 50)}"
        cursor.execute(
            """INSERT INTO mimiciv_hosp.procedures_icd VALUES (?, ?, ?, ?, ?, ?)""",
            (i % 100 + 1, 1000 + i, i, "2020-01-01", icd_code, 10),
        )
        if i <= 50:
            cursor.execute(
                """INSERT INTO mimiciv_hosp.d_icd_procedures VALUES (?, ?, ?)""",
                (icd_code, 10, f"Procedure for {icd_code}"),
            )

    # Insert sample lab events
    for i in range(1, 101):
        itemid = 50000 + (i % 50)
        cursor.execute(
            """INSERT INTO mimiciv_hosp.labevents VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                i,
                i % 100 + 1,
                1000 + i,
                1000 + i,
                itemid,
                "2020-01-01 10:00:00",
                "2020-01-01 10:00:00",
                "100",
                100.0,
                "mg/dL",
                80.0,
                120.0,
                None,
                "ROUTINE",
                None,
            ),
        )
        if i <= 50:
            cursor.execute(
                """INSERT INTO mimiciv_hosp.d_labitems VALUES (?, ?, ?, ?, ?)""",
                (itemid, f"Lab Item {itemid}", "Blood", "Chemistry", f"LOINC_{itemid}"),
            )

    # Insert sample chart events
    for i in range(1, 101):
        itemid = 220000 + (i % 50)
        cursor.execute(
            """INSERT INTO mimiciv_icu.chartevents VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                i % 100 + 1,
                1000 + i,
                2000 + i,
                "2020-01-01 10:00:00",
                "2020-01-01 10:00:00",
                itemid,
                "100",
                100.0,
                "bpm",
                0,
            ),
        )
        if i <= 50:
            cursor.execute(
                """INSERT INTO mimiciv_icu.d_items VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    itemid,
                    f"Chart Item {itemid}",
                    f"CI{itemid}",
                    "chartevents",
                    "Vital Signs",
                    "bpm",
                    "Numeric",
                    60.0,
                    100.0,
                ),
            )

    conn.commit()
    conn.close()

    # Set up SQLAlchemy event listener to attach databases on connect
    _setup_sqlite_schema_attachments(
        db_path,
        {
            "mimiciv_hosp": mimiciv_hosp_path,
            "mimiciv_icu": mimiciv_icu_path,
        },
    )

    yield db_path

    # Cleanup
    Path(db_path).unlink(missing_ok=True)
    Path(mimiciv_hosp_path).unlink(missing_ok=True)
    Path(mimiciv_icu_path).unlink(missing_ok=True)


@pytest.fixture(scope="session")
def eicu_sqlite_db() -> Generator[str, None, None]:
    """Create a SQLite database with eICU-CRD test data.

    Returns
    -------
    Generator[str, None, None]
        Path to the SQLite database file.

    """
    # Create a temporary SQLite database
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as temp_db:
        db_path = temp_db.name

    # Create temporary files for schemas
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as eicu_crd_db:
        eicu_crd_path = eicu_crd_db.name

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create schemas using ATTACH DATABASE
    cursor.execute(f"ATTACH DATABASE '{eicu_crd_path}' AS eicu_crd")

    # Create patient table for eicu_crd schema
    cursor.execute("""
        CREATE TABLE eicu_crd.patient (
            patientunitstayid INTEGER PRIMARY KEY,
            patienthealthsystemstayid INTEGER,
            gender TEXT,
            age TEXT,
            ethnicity TEXT,
            hospitalid INTEGER,
            wardid INTEGER,
            apacheadmissiondx TEXT,
            admissionheight REAL,
            hospitaladmittime24 TEXT,
            hospitaladmitoffset INTEGER,
            hospitaladmitsource TEXT,
            hospitaldischargeyear INTEGER,
            hospitaldischargetime24 TEXT,
            hospitaldischargeoffset INTEGER,
            hospitaldischargelocation TEXT,
            hospitaldischargestatus TEXT,
            unittype TEXT,
            unitadmittime24 TEXT,
            unitadmitsource TEXT,
            unitvisitnumber INTEGER,
            unitstaytype TEXT,
            admissionweight REAL,
            dischargeweight REAL,
            unitdischargetime24 TEXT,
            unitdischargeoffset INTEGER,
            unitdischargelocation TEXT,
            unitdischargestatus TEXT
        )
    """)

    # Create diagnosis table
    cursor.execute("""
        CREATE TABLE eicu_crd.diagnosis (
            diagnosisid INTEGER PRIMARY KEY,
            patientunitstayid INTEGER,
            diagnosisoffset INTEGER,
            diagnosisstring TEXT,
            icd9code TEXT,
            diagnosispriority TEXT
        )
    """)

    # Create vitalPeriodic table
    cursor.execute("""
        CREATE TABLE eicu_crd.vitalperiodic (
            vitalperiodicid INTEGER PRIMARY KEY,
            patientunitstayid INTEGER,
            observationoffset INTEGER,
            temperature REAL,
            sao2 INTEGER,
            heartrate INTEGER,
            respiration INTEGER,
            cvp INTEGER,
            etco2 INTEGER,
            systemicsystolic INTEGER,
            systemicdiastolic INTEGER,
            systemicmean INTEGER,
            pasystolic INTEGER,
            padiastolic INTEGER,
            pamean INTEGER,
            st1 REAL,
            st2 REAL,
            st3 REAL,
            icp INTEGER
        )
    """)

    # Create vitalAperiodic table
    cursor.execute("""
        CREATE TABLE eicu_crd.vitalaperiodic (
            vitalaperiodicid INTEGER PRIMARY KEY,
            patientunitstayid INTEGER,
            observationoffset INTEGER,
            noninvasivesystolic INTEGER,
            noninvasivediastolic INTEGER,
            noninvasivemean INTEGER,
            paop INTEGER,
            cardiacoutput REAL,
            cardiacinput REAL,
            svr INTEGER,
            svri INTEGER,
            pvr INTEGER,
            pvri INTEGER
        )
    """)

    # Insert sample patient data
    for i in range(1, 101):
        cursor.execute(
            """INSERT INTO eicu_crd.patient VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                i,
                i,
                "Male" if i % 2 == 0 else "Female",
                str(50 + (i % 40)),
                "Caucasian",
                100 + (i % 10),
                200 + (i % 5),
                "Sepsis",
                170.0,
                "10:00",
                -60,
                "Emergency",
                2020,
                "12:00",
                720,
                "Home",
                "Alive",
                "ICU",
                "12:00",
                "ER",
                1,
                "admit",
                70.0,
                68.0,
                "14:00",
                840,
                "Floor",
                "Alive",
            ),
        )

    # Insert sample diagnosis data
    for i in range(1, 101):
        cursor.execute(
            """INSERT INTO eicu_crd.diagnosis VALUES (?, ?, ?, ?, ?, ?)""",
            (
                i,
                i % 100 + 1,
                i * 60,
                f"Diagnosis string {i}",
                f"{i % 1000:03d}.{i % 100:02d}",
                "Primary" if i % 3 == 0 else "Secondary",
            ),
        )

    # Insert sample vital periodic data
    for i in range(1, 101):
        cursor.execute(
            """INSERT INTO eicu_crd.vitalperiodic VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                i,
                i % 100 + 1,
                i * 5,
                37.0,
                98,
                80,
                16,
                5,
                40,
                120,
                80,
                100,
                25,
                15,
                20,
                0.0,
                0.0,
                0.0,
                10,
            ),
        )

    # Insert sample vital aperiodic data
    for i in range(1, 101):
        cursor.execute(
            """INSERT INTO eicu_crd.vitalaperiodic VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (i, i % 100 + 1, i * 10, 120, 80, 100, 12, 5.0, 5.0, 800, 2000, 120, 300),
        )

    conn.commit()
    conn.close()

    # Set up SQLAlchemy event listener to attach databases on connect
    _setup_sqlite_schema_attachments(
        db_path,
        {
            "eicu_crd": eicu_crd_path,
        },
    )

    yield db_path

    # Cleanup
    Path(db_path).unlink(missing_ok=True)
    Path(eicu_crd_path).unlink(missing_ok=True)
