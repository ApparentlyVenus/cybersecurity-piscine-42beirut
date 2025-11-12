BASE_IMAGE = inquisitor-base

build: 
	docker build -t $(BASE_IMAGE) .

up: build
	docker compose up -d

down: 
	docker compose down

clean: down
	docker rmi $(BASE_IMAGE)

ping:
	docker compose exec victim ping -c 1 172.20.0.3
	docker compose exec victim ping -c 1 172.20.0.99
	docker compose exec router ping -c 1 172.20.0.10
	docker compose exec router ping -c 1 172.20.0.99

router-arp:
	docker compose exec router arp 

victim-arp:
	docker compose exec router arp 