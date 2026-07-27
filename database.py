# 2026-07-26 MC: Created file

import psycopg
from sshtunnel import SSHTunnelForwarder
import json


class PostgresDatabase:
    """
    Handles SSH tunnel creation and PostgreSQL connections.
    """

    def __init__(self, config_path="./Options_pipeline/config.json"):
        # Load configuration
        with open(config_path, "r") as file:
            config = json.load(file)

        # SSH information
        self.ec2_host = config["ssh"]["host"]
        self.ec2_user = config["ssh"]["user"]
        self.ssh_key = config["ssh"]["key path"]

        # Database information
        self.db_name = config["database"]["name"]
        self.db_user = config["database"]["user"]
        self.db_password = config["database"]["password"]

        self.tunnel = None
        self.conn = None


    def connect(self):
        """
        Creates SSH tunnel and PostgreSQL connection.
        """

        self.tunnel = SSHTunnelForwarder(
            (self.ec2_host, 22),
            ssh_username=self.ec2_user,
            ssh_pkey=self.ssh_key,
            remote_bind_address=("localhost", 5432)
        )

        self.tunnel.start()

        print("SSH tunnel created")

        self.conn = psycopg.connect(
            host="localhost",
            port=self.tunnel.local_bind_port,
            dbname=self.db_name,
            user=self.db_user,
            password=self.db_password
        )

        print("Connected to PostgreSQL!")

        return self.conn.cursor()


    def close(self):
        """
        Closes database resources.
        """

        if self.conn:
            self.conn.close()

        if self.tunnel:
            self.tunnel.stop()

        print("Database connection closed")