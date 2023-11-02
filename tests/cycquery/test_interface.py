"""Test functions for interface module in query package."""

import os
import shutil
from typing import Generator
from unittest.mock import patch

import pandas as pd
import pytest

from cycquery.interface import QueryInterface
from cycquery.omop import OMOPQuerier


@pytest.fixture()
def test_data():
    """Dummy dataframe for testing."""
    return pd.DataFrame([[1, "a", 1], [5.1, "b", 0]], columns=["col1", "col2", "col3"])


@patch("cycquery.orm.Database")
@patch("sqlalchemy.sql.selectable.Subquery")
def test_query_interface(
    database,
    query,
    test_data,
):
    """Test QueryInterface."""
    query_interface = QueryInterface(database, query)
    query_interface.run()

    query_interface._data = test_data
    path = os.path.join("test_save", "test_features.parquet")
    query_interface.save(path)
    loaded_data = pd.read_parquet(path)
    assert loaded_data.equals(test_data)
    shutil.rmtree("test_save")
    query_interface.clear_data()
    assert not query_interface.data

    with pytest.raises(ValueError):
        query_interface.save(path, file_format="donkey")


@pytest.mark.integration_test()
def test_query_interface_integration():
    """Test QueryInterface with OMOPQuerier."""
    synthea = OMOPQuerier(
        database="synthea_integration_test",
        schema_name="cdm_synthea10",
        user="postgres",
        password="pwd",
    )
    visits = synthea.visit_occurrence()
    assert isinstance(visits, QueryInterface)
    visits_df = visits.run()
    assert isinstance(visits_df, pd.DataFrame)
    assert visits_df.shape[0] > 0

    # Test running batched query.
    visits_df_batches = visits.run(
        index_col="visit_occurrence_id",
        batch_mode=True,
        batch_size=1000,
    )
    assert isinstance(visits_df_batches, Generator)
    visits_df_batch = next(visits_df_batches)
    assert isinstance(visits_df_batch, pd.DataFrame)
    assert "visit_occurrence_id" in visits_df_batch.columns
    visits_df_next_batch = next(visits_df_batches)
    visit_ids_0 = visits_df_batch["visit_occurrence_id"]
    visit_ids_1 = visits_df_next_batch["visit_occurrence_id"]
    # check that the partitions don't overlap
    assert len(set(visit_ids_0).intersection(set(visit_ids_1))) == 0

    # test running a query using SQL string
    synthea_db = visits.database
    visits_df = synthea_db.run_query("SELECT * FROM cdm_synthea10.visit_occurrence")
    assert isinstance(visits_df, pd.DataFrame)
    assert visits_df.shape[0] > 0
