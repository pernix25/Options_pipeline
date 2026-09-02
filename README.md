# Options_pipeline
Production-style financial data pipeline built with Python, PostgreSQL, and AWS. Automatically ingests stock and options market data through a modular ETL process and stores it in a PostgreSQL database on an AWS EC2 instance, enabling scalable data engineering and historical market analysis.

Apache Airflow is used to orchestrate and schedule the pipeline, providing automated execution, monitoring, logging, and failure tracking through the Airflow web interface. The core ETL logic is contained within a modular Python ETLPipeline class, while the Airflow DAG manages when and how the pipeline is executed.

Getting Started:
  Update the keys in config.template.json to your own AWS EC2 & Postgres information, then rename the file to 'config.json'.

  After configuring Airflow and placing the DAG in the Airflow DAGs directory, the options_pipeline DAG can be started and monitored through the Airflow web interface.
