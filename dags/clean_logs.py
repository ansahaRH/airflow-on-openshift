from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash_operator import BashOperator

# Define default_args dictionary to specify the default parameters of the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
}

# Instantiate a DAG with the defined default_args
dag = DAG(
    'clean_airflow_logs',
    default_args=default_args,
    description='DAG to clean Airflow logs',
    schedule_interval=timedelta(minutes=15),  # Set the schedule interval
)

# Define the BashOperator task
clean_logs_task = BashOperator(
    task_id='clean_logs',
    bash_command="""
        set -euo pipefail
        readonly DIRECTORY="${AIRFLOW_HOME:-/usr/local/airflow}"
        readonly RETENTION="${AIRFLOW__LOG_RETENTION_DAYS:-15}"

        trap "exit" INT TERM

        readonly EVERY=$((15*60))

        echo "Cleaning logs every $EVERY seconds"

        while true; do
          echo "Trimming airflow logs to ${RETENTION} days."
          find "${DIRECTORY}"/logs \
            -type d -name 'lost+found' -prune -o \
            -type f -mtime +"${RETENTION}" -name '*.log' -print0 | \
            xargs -0 rm -f

          find "${DIRECTORY}"/logs -type d -empty -delete || true

          seconds=$(( $(date -u +%s) % EVERY))
          (( seconds < 1 )) || sleep $((EVERY - seconds - 1))
          sleep 1
        done
    """,
    dag=dag,
)

# Set task dependencies if any
# clean_logs_task >> some_other_task

if __name__ == "__main__":
    dag.cli()

