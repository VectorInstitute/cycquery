"""Test cycquery.orm module."""

import os
import sqlite3

import pandas as pd
import pytest

from cycquery import DatasetQuerier, OMOPQuerier
from cycquery.orm import _get_db_url


# Function to create and populate the database
def create_dummy_database(db_file):
    """Create dummy database file."""
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Create a table
    cursor.execute(
        """CREATE TABLE test_table (
                        id INTEGER PRIMARY KEY,
                        name TEXT,
                        age INTEGER
                      )""",
    )

    # Insert dummy data
    dummy_data = [(1, "Alice", 30), (2, "Bob", 25), (3, "Charlie", 35)]
    cursor.executemany(
        "INSERT INTO test_table (id, name, age) VALUES (?, ?, ?)",
        dummy_data,
    )

    # Save (commit) the changes and close the connection
    conn.commit()
    conn.close()


def test_dataset_querier():
    """Test DatasetQuerier."""
    db_file = "test_database.db"

    # Ensure database file doesn't exist before test
    if os.path.exists(db_file):
        os.remove(db_file)

    create_dummy_database(db_file)

    # Test DatasetQuerier
    querier = DatasetQuerier(
        dbms="sqlite",
        database=db_file,
    )
    assert querier is not None
    test_table = querier.main.test_table().run()
    assert len(test_table) == 3
    assert test_table["name"].tolist() == ["Alice", "Bob", "Charlie"]
    assert test_table["age"].tolist() == [30, 25, 35]

    # Clean up: remove the database file after testing
    os.remove(db_file)


def test_get_db_url():
    """Test _get_db_url."""
    # Test for a typical SQL database (e.g., PostgreSQL, MySQL)
    assert (
        _get_db_url("postgresql", "user", "pass", "localhost", 5432, "mydatabase")
        == "postgresql://user:pass@localhost:5432/mydatabase"
    )
    assert (
        _get_db_url("mysql", "root", "rootpass", "dbhost", 3306, "somedb")
        == "mysql://root:rootpass@dbhost:3306/somedb"
    )

    # Test for SQLite database file
    assert _get_db_url("sqlite", database="mydatabase.db") == "sqlite:///mydatabase.db"

    # Test handling of empty parameters for typical SQL databases
    assert _get_db_url("mysql", "", "", "", None, "") == "mysql://:@:None/"

    # Test handling of None for port
    assert (
        _get_db_url("postgresql", "user", "pass", "localhost", None, "mydatabase")
        == "postgresql://user:pass@localhost:None/mydatabase"
    )

    # Test case insensitivity for DBMS
    assert _get_db_url("SQLITE", database="mydatabase.db") == "sqlite:///mydatabase.db"

    # Test for incorrect usage
    with pytest.raises(
        ValueError,
    ):
        _get_db_url("unknown_dbms", "user", "pass", "localhost", 1234, "mydatabase")


@pytest.mark.integration_test()
def test_omop_querier():
    """Test ORM using OMOPQuerier."""
    querier = OMOPQuerier(
        database="synthea_integration_test",
        schema_name="cdm_synthea10",
        user="postgres",
        password="pwd",
    )
    assert querier is not None
    db_ = querier.db
    visits_query = querier.visit_occurrence().query
    db_.save_query_to_csv(visits_query, "visits.csv")
    visits_df = pd.read_csv("visits.csv")
    assert len(visits_df) == 4320
    os.remove("visits.csv")

    db_.save_query_to_parquet(visits_query, "visits.parquet")
    visits_df = pd.read_parquet("visits.parquet")
    assert len(visits_df) == 4320
    os.remove("visits.parquet")
