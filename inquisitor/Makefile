build:
	docker build -t inquisitor-base .

up:
	docker-compose up -d

down:
	docker-compose down

clean:
	docker-compose down

fclean: clean
	docker-compose down -v
	docker rmi inquisitor-base 2>/dev/null || true
	rm -rf ftp_data

re: fclean build

demo: build up
	@echo "\n=== Inquisitor Environment Ready ==="
	@sleep 2
	@echo "\nRouter:   172.20.0.3"
	@echo "Victim:   172.20.0.10"
	@echo "Attacker: 172.20.0.99"
	@echo "\nGet MACs:"
	@echo "  docker exec router ip link show eth0 | grep ether"
	@echo "  docker exec victim ip link show eth0 | grep ether"
	@echo "\nEnable forwarding:"
	@echo "  docker exec attacker sysctl -w net.ipv4.ip_forward=1"
	@echo "\nRun attack:"
	@echo "  docker exec -it attacker python3 /app/inquisitor.py 172.20.0.3 <R_MAC> 172.20.0.10 <V_MAC>"
	@echo ""

.PHONY: build up down clean fclean re demo
