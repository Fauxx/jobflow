#!/bin/bash
echo "Waiting for PostgreSQL to be ready..."
until ./venv/bin/python -c "import psycopg2; psycopg2.connect('postgresql://jobflow:password@localhost:5432/jobflow')" 2>/dev/null; do
  sleep 2
done
echo "PostgreSQL is ready! Running migrations..."
./venv/bin/alembic revision --autogenerate -m "Initial schema"
./venv/bin/alembic upgrade head
