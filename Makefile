.PHONY: test

test:
	mkdir -p reports/
	pytest --cov=bateman --junitxml=reports/pytest.xml || true
	pylint --exit-zero --disable=R,C --output-format=parseable --reports=y ./bateman > reports/pylint.log
