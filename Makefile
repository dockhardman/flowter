install_dev:
	poetry install -E all

upgrade_dependencies:
	poetry update
	poetry export --without-hashes -f requirements.txt --output requirements.txt

format_all:
	isort . --skip setup.py
	black --exclude setup.py .
