.PHONY: install run test clean docker-build docker-run

install:
	pip install -r requirements.txt

run:
	python app.py

test:
	python -m pytest tests/ -v 2>/dev/null || echo "No tests configured"

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null; \
	find . -type f -name "*.pyc" -delete 2>/dev/null; \
	find . -type d -name .ipynb_checkpoints -exec rm -rf {} + 2>/dev/null; \
	rm -rf dist/ build/ *.egg-info/ .pytest_cache/; \
	rm -f EventsLog.log; \
	true

docker-build:
	docker build -t event-driven-automation .

docker-run:
	docker run --env-file .env event-driven-automation
