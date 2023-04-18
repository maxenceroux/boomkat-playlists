build-docker:
	docker-compose build

build-docker-arm:
	docker-compose -f docker-compose.arm.yml build

start-docker-arm:
	docker-compose -f docker-compose.arm.yml up -d

start-docker:
	docker-compose up -d

stop-docker:
	docker-compose down

