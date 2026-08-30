# 2026-07-28 MC: Created file

# Ideas
# move caching, getting contract, and getting contract prices into pipeline methods

from database import PostgresDatabase
from poly import PolygonClient

class ETLPipeline:
    def __init__(
            self
            , database: PostgresDatabase
            , polygon_client: PolygonClient
        ) -> None:
        
        self.db = database
        self.polygon = polygon_client

    def start(self) -> None:
        """
        Starts the ETL pipeline by establishing a database connection.

        Creates a PostgreSQL cursor that will be used throughout the ETL
        process for executing SQL statements.
        """
        self.cursor = self.db.connect()
