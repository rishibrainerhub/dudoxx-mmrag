#!/bin/sh


maybe_install () {
  # TODO: `-nt` may not be supported on some systems...
  if [ ! -d .venv ] || [ \( Pipfile -nt .venv \) ] || [ \( Pipfile.lock -nt .venv \) ]; then
    set -x
    pipenv sync --dev
    set +x
  fi
}

while [ $# -gt 0 ]; do
  case "$1" in
    migrate )  ## apply the database migrations
        maybe_install
        set -x
        python -m alembic upgrade head || { echo "Migration failed"; exit 1; }
        set +x
        ;;
    run )  ## run the dev server
        maybe_install
        set -x
        python -m dudoxx || { echo "Failed to run server"; exit 1; }
        set +x
        ;;
    lint )  ## check for code issues
        maybe_install
        set -x
        black --check . || { echo "Linting failed"; exit 1; }
        set +x
        ;;
    reformat )  ## automatically fix code issues where possible
        maybe_install
        set -x    
        black . || { echo "Reformatting failed"; exit 1; }
        set +x
        ;;
    api-test )  ## run the API tests
        maybe_install
        set -x
        pytest tests/api || { echo "API tests failed"; exit 1; }
        set +x
        ;;
    service-test )  ## run the service tests
        maybe_install
        set -x
        pytest tests/services || { echo "Service tests failed"; exit 1; }
        set +x
        ;;
    help )  ## display help message
      echo "Available commands:"
      echo "  migrate      Apply the database migrations"
      echo "  run         Run the dev server"
      echo "  lint        Check for code issues"
      echo "  reformat    Automatically fix code issues"
      echo "  api-test    Run the API tests"
      echo "  service-test Run the service tests"
      ;;
    * )
      echo "Unrecognised argument: $1"
      exit 1
      ;;
  esac
  shift
done
