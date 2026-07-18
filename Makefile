.PHONY: setup lint test terraform-fmt terraform-validate generate-sample validate-sample create-user-facts analyze-ab-test dashboard

setup:
	python3 -m venv .venv
	. .venv/bin/activate && pip install --upgrade pip
	. .venv/bin/activate && pip install -r requirements-dev.txt

lint:
	. .venv/bin/activate && ruff check .

test:
	. .venv/bin/activate && pytest

terraform-fmt:
	terraform fmt -recursive terraform

terraform-validate:
	cd terraform/environments/dev && terraform init && terraform validate

generate-sample:
	. .venv/bin/activate && python app/event_generator/generate_events.py --num-users 5000

validate-sample:
	. .venv/bin/activate && python app/event_generator/validate_events.py

create-user-facts:
	. .venv/bin/activate && python pipelines/transform_events/transform_raw_to_parquet.py

analyze-ab-test:
	. .venv/bin/activate && python pipelines/analyze_experiment/analyze_ab_test.py

dashboard:
	. .venv/bin/activate && streamlit run dashboard/streamlit_app.py
