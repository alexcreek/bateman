.PHONY: test build

image := 192.168.1.10:4000/bateman:latest

test:
	mkdir -p reports/
	pytest --cov=bateman --junitxml=reports/pytest.xml || true
	pylint --exit-zero --disable=R,C --output-format=parseable --reports=y ./bateman > reports/pylint.log

build:
	docker build . -t 192.168.1.10:4000/bateman:latest
	docker push ${image}
