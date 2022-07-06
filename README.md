# Airflow Local

## Running

[Running Airflow in Docker](<https://airflow.apache.org/docs/apache-airflow/stable/start/docker.html>) 

The default username and password is "airflow"

```sh
# Initialize database
docker-compose up airflow-init

# Start
docker-compose up
```

## Cleanup

[Full cleanup instructions](<https://airflow.apache.org/docs/apache-airflow/stable/start/docker.html#cleaning-up-the-environment>)

```sh
docker-compose down --volumes --remove-orphans
```