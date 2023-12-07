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
    schedule_interval=timedelta(minutes=1),  # Set the schedule interval
)

# Define the BashOperator task
clean_logs_task = BashOperator(
    task_id='clean_logs',
    bash_command="""
        set -euo pipefail
        readonly PVC_DIRECTORY="/volumes/csi/csi-vol-12d336e7-5ccf-4fef-9e3b-faf18dd8809f/9585e4a3-199f-4c44-aae0-d433490cb7c4l"
        readonly RETENTION="${AIRFLOW__LOG_RETENTION_DAYS:-0}"

        trap "exit" INT TERM

        echo "Cleaning logs older than ${RETENTION} days."
        find "${PVC_DIRECTORY}"/logs \
            -type f -mtime +"${RETENTION}" -name '*.log' -print0 | \
            xargs -0 rm -f
    """,
    dag=dag,
)

# Set task dependencies if any
# clean_logs_task >> some_other_task

if __name__ == "__main__":
    dag.cli()
