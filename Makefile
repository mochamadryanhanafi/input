.PHONY: run build stop

run:
	@docker compose up -d

build:
	@docker compose build

stop:
	@docker compose down
