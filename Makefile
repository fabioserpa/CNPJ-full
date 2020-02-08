# Execution application python
python-run:
	docker-compose up --build

# Execution elasticsearch container
elasticsearch-run:
	docker-compose -f docker-compose-elk.yml up -d --build elasticsearch

# Execution kibana container
kibana-run:
	docker-compose -f docker-compose-elk.yml up -d --build kibana

# Execution container elasticsearch and kibana
ek-run: elasticsearch-run kibana-run

# Execution logstash container
logstash-run:
	docker-compose -f docker-compose-elk.yml up --build logstash

# Execution all container elk
elk-run: elasticsearch-run kibana-run logstash-run