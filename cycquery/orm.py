"""Object Relational Mapper (ORM) using sqlalchemy."""

import csv
import logging
import os
import socket
from dataclasses import dataclass
from typing import Dict, Generator, List, Optional, Union
from urllib.parse import quote_plus

import pandas as pd
import pyarrow.csv as pv
import pyarrow.parquet as pq
from sqlalchemy import MetaData, and_, create_engine, func, inspect, select
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session
from sqlalchemy.sql.elements import BinaryExpression, BooleanClauseList
from sqlalchemy.sql.selectable import Select, Subquery

from cycquery.util import (
    DBSchema,
    DBTable,
    TableTypes,
    get_attr_name,
    get_column,
    table_params_to_type,
)
from cycquery.utils.file import exchange_extension, process_file_save_path
from cycquery.utils.log import setup_logging
from cycquery.utils.profile import time_function


# Logging.
LOGGER = logging.getLogger(__name__)
setup_logging(print_level="INFO", logger=LOGGER)


SOCKET_CONNECTION_TIMEOUT = 5


def _get_db_url(
    dbms: str,
    user: str = "",
    pwd: str = "",
    host: str = "",
    port: Optional[int] = None,
    database: str = "",
) -> str:
    """
    Generate a database connection URL.

    This function constructs a URL for database connection, which is compatible
    with various database management systems (DBMS), including support for SQLite
    database files.

    Parameters
    ----------
    dbms : str
        The database management system type (e.g., 'postgresql', 'mysql', 'sqlite').
    user : str, optional
        The username for the database, by default empty. Not used for SQLite.
    pwd : str, optional
        The password for the database, by default empty. Not used for SQLite.
    host : str, optional
        The host address of the database, by default empty. Not used for SQLite.
    port : int, optional
        The port number for the database, by default None. Not used for SQLite.
    database : str, optional
        The name of the database or the path to the database file (for SQLite),
        by default empty.

    Returns
    -------
    str
        A string representing the database connection URL. For SQLite,
        it returns a URL in the format 'sqlite:///path_to_database.db'.
        For other DBMS types, it returns a URL in the
        format 'dbms://user:password@host:port/database'.

    Examples
    --------
    >>> _get_db_url('postgresql', 'user', 'pass', 'localhost', 5432, 'mydatabase')
    'postgresql://user:pass@localhost:5432/mydatabase'

    >>> _get_db_url('sqlite', database='path_to_database.db')
    'sqlite:///path_to_database.db'

    """
    if dbms.lower() not in ["postgresql", "mysql", "sqlite"]:
        raise ValueError(
            f"Database management system '{dbms}' is not supported, "
            f"please use one of 'postgresql', 'mysql', or 'sqlite'.",
        )
    if dbms.lower() == "sqlite":
        return f"sqlite:///{database}"  # SQLite expects a file path as the database parameter

    return f"{dbms}://{user}:{quote_plus(pwd)}@{host}:{str(port)}/{database}"


@dataclass
class DatasetQuerierConfig:
    """Configuration for the dataset querier.

    Attributes
    ----------
    dbms : str
        The database management system type (e.g., 'postgresql', 'mysql', 'sqlite').
    user : str, optional
        The username for the database, by default empty. Not used for SQLite.
    pwd : str, optional
        The password for the database, by default empty. Not used for SQLite.
    host : str, optional
        The host address of the database, by default empty. Not used for SQLite.
    port : int, optional
        The port number for the database, by default None. Not used for SQLite.
    database : str, optional
        The name of the database or the path to the database file (for SQLite),
        by default empty.

    """

    dbms: str
    user: str = ""
    password: str = ""
    host: str = ""
    port: Optional[int] = None
    database: str = ""


class Database:
    """Database class.

    Attributes
    ----------
    config
        Configuration stored in a dataclass.
    engine
        SQL extraction engine.
    inspector
        Module for schema inspection.
    session
        Session for ORM.
    is_connected
        Whether the database is setup, connected and ready to run queries.

    """

    def __init__(self, config: DatasetQuerierConfig) -> None:
        """Instantiate.

        Parameters
        ----------
        config
            Path to directory with config file, for overrides.

        """
        self.config = config
        self.is_connected = False

        # Check if server is up or database file exists.
        if self.config.dbms.lower() == "sqlite":
            if not os.path.exists(self.config.database):
                LOGGER.error(
                    f"""Database file '{self.config.database}' does not exist!""",
                )
                return
        else:
            if not self.config.host:
                LOGGER.error("""No server host provided!""")
                return
            if not self.config.port:
                LOGGER.error("""No server port provided!""")
                return
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(SOCKET_CONNECTION_TIMEOUT)
            try:
                is_port_open = sock.connect_ex((self.config.host, self.config.port))
            except socket.gaierror:
                LOGGER.error("""Server name not known, cannot establish connection!""")
                return
            if is_port_open:
                LOGGER.error(
                    """Valid server host but port seems open, check if server is up!""",
                )
                return

        self.engine = self._create_engine()
        self.session = self._create_session()
        self._tables: List[str] = []
        self._setup()
        self.is_connected = True
        LOGGER.info("Database setup, ready to run queries!")

    def _create_engine(self) -> Engine:
        """Create an engine."""
        self.conn = _get_db_url(
            self.config.dbms,
            self.config.user,
            self.config.password,
            self.config.host,
            self.config.port,
            self.config.database,
        )
        return create_engine(
            _get_db_url(
                self.config.dbms,
                self.config.user,
                self.config.password,
                self.config.host,
                self.config.port,
                self.config.database,
            ),
        )

    def _create_session(self) -> Session:
        """Create session."""
        self.inspector = inspect(self.engine)

        # Create a session for using ORM.
        session = sessionmaker(self.engine)
        session.configure(bind=self.engine)

        return session()

    def list_tables(self) -> List[str]:
        """List tables in a schema.

        Returns
        -------
        List[str]
            List of table names.

        """
        return self._tables

    def _setup(self) -> None:
        """Prepare ORM DB."""
        meta: Dict[str, MetaData] = {}
        schemas = self.inspector.get_schema_names()
        for schema_name in schemas:
            metadata = MetaData(schema=schema_name)
            metadata.reflect(bind=self.engine)
            meta[schema_name] = metadata
            schema = DBSchema(schema_name, meta[schema_name])
            for table_name in meta[schema_name].tables:
                table = DBTable(table_name, meta[schema_name].tables[table_name])
                for column in meta[schema_name].tables[table_name].columns:
                    setattr(table, column.name, column)
                if not isinstance(table.name_, str):
                    table.name_ = str(table.name_)
                self._tables.append(table.name_)
                setattr(schema, get_attr_name(table.name_), table)
            setattr(self, schema_name, schema)

    @time_function
    @table_params_to_type(Select)
    def run_query(
        self,
        query: Union[TableTypes, str],
        dtype_backend: str = "pyarrow",
        limit: Optional[int] = None,
        index_col: Optional[str] = None,
    ) -> pd.DataFrame:
        """Run query.

        Parameters
        ----------
        query
            Query to run.
        dtype_backend
            Backend for dtype conversion.
        limit
            Limit query result to limit.
        index_col
            Column which becomes the index, and defines the partitioning.
            Should be a indexed column in the SQL server, and any orderable type.

        Returns
        -------
        pandas.DataFrame
            Extracted data from query.

        """
        if isinstance(query, str) and limit is not None:
            raise ValueError(
                "Cannot use limit argument when running raw SQL string query!",
            )
        # Limit the results returned.
        if limit is not None:
            query = query.limit(limit)  # type: ignore

        # Run the query and return the results.
        with self.session.connection():
            data = pd.read_sql_query(
                query,
                self.engine,
                index_col=index_col,
                dtype_backend=dtype_backend,
            )
        LOGGER.info("Query returned successfully!")

        return data

    @time_function
    @table_params_to_type(Select)
    def save_query_to_csv(self, query: TableTypes, path: str) -> str:
        """Save query in a .csv format.

        Parameters
        ----------
        query
            Query to save.
        path
            Save path.

        Returns
        -------
        str
            Processed save path for upstream use.

        """
        path = process_file_save_path(path, "csv")

        with self.session.connection():
            result = self.engine.execute(query)
            with open(path, "w", encoding="utf-8") as file_descriptor:
                outcsv = csv.writer(file_descriptor)
                outcsv.writerow(result.keys())
                outcsv.writerows(result)

        return path

    @time_function
    @table_params_to_type(Select)
    def save_query_to_parquet(self, query: TableTypes, path: str) -> str:
        """Save query in a .parquet format.

        Parameters
        ----------
        query
            Query to save.
        path
            Save path.

        Returns
        -------
        str
            Processed save path for upstream use.

        """
        path = process_file_save_path(path, "parquet")

        # Save to CSV, load with pyarrow, save to Parquet
        csv_path = exchange_extension(path, "csv")
        self.save_query_to_csv(query, csv_path)
        table = pv.read_csv(csv_path)
        os.remove(csv_path)
        pq.write_table(table, path)

        return path

    def _query_batch_conditions(
        self,
        query: TableTypes,
        index_col: str,
        batch_size: int,
    ) -> List[Union[BinaryExpression, BooleanClauseList]]:
        """Return a list of WHERE conditions to segment a query into batches.

        Batches are created via SQL windowing, based on segmenting the values in a
        given column, such as an ID column, into intervals.

        Requires a database that supports window functions.

        Parameters
        ----------
        query
            Query to run.
        index_col
            Name of the sample ID column by which to batch.
        batch_size
            Batch size for the query.

        Returns
        -------
        list of sqlalchemy.sql.elements.BinaryExpression or
        sqlalchemy.sql.elements.BooleanClauseList
            The window conditions on which to filter.

        """

        def _compute_query_dividers(
            query: Subquery,
            index_col: str,
            maximum: int,
        ) -> List[int]:
            # Compute the row count for each unique value
            col = get_column(query, index_col)
            table = select(col, func.count(col).label("count")).group_by(col)
            count_data = self.run_query(table)

            # Check that all values can actually fit into the maximum batch size
            max_count = count_data["count"].max()
            if maximum < max_count:
                raise ValueError(f"Maximum must be at least {max_count}.")

            # Sort and create a cumulative sum of row counts
            count_data = count_data.sort_values(index_col)
            count_data["cumsum"] = count_data["count"].cumsum()

            # Create query dividers
            last_sum = 0

            if len(count_data) == 0:
                raise ValueError("Query is empty. Cannot return batched results.")

            dividers = [int(count_data[index_col].iloc[0])]
            for i, cumsum in enumerate(count_data["cumsum"].values[1:]):
                # If adding the next value will put the sum over the max,
                # then add another divider on the previous value
                if cumsum - last_sum > maximum:
                    dividers.append(int(count_data[index_col].iloc[i]))
                    last_sum = count_data["cumsum"].iloc[i]

            return dividers

        def _range_condition(
            start_id: int,
            end_id: Optional[int] = None,
        ) -> Union[BinaryExpression, BooleanClauseList]:
            if end_id:
                return and_(column >= start_id, column < end_id)

            return column >= start_id

        # Create interval dividers
        dividers = _compute_query_dividers(query, index_col, batch_size)

        # Create filtering conditions
        column = get_column(query, index_col)
        conditions = []
        while dividers:
            # Create interval ranges
            start = dividers.pop(0)
            end = dividers[0] if dividers else None

            # Create condition
            conditions.append(_range_condition(start, end))

        return conditions

    @table_params_to_type(Subquery)
    def run_query_batch(
        self,
        query: TableTypes,
        index_col: str,
        batch_size: int,
        dtype_backend: str = "pyarrow",
    ) -> Generator[pd.DataFrame, None, None]:
        """Generate query batches with complete sets of IDs in a batch.

        Queries are sorted and grouped such that the rows for a given sample ID are kept
        together in a single batch.

        Parameters
        ----------
        query
            Query to run.
        index_col
            Name of the sample ID column by which to batch.
        batch_size
            Batch size for the query. Since the partitioning happens on the index
            column, the batch size is the approximate number of rows that will
            be returned in a batch.
        dtype_backend
            Backend for dtype conversion.

        Yields
        ------
        pandas.DataFrame
            A query batch with complete sets of sample IDs.

        """
        if "limit" in str(query).lower():
            raise NotImplementedError(
                "Currently not supporting batching for queries with a LIMIT.",
            )

        conditions = self._query_batch_conditions(query, index_col, batch_size)
        sess_query = self.session.query(query)

        # Opportunity for easy multi-processing/parallelization here!
        for condition in conditions:
            run = (sess_query.filter(condition)).subquery()
            yield pd.read_sql_query(run, self.engine, dtype_backend=dtype_backend)
