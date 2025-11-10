IMAGE_NAME = stockholm_image
CONTAINER_NAME = stockholm_container
TARGET_DIR = $(HOME)/infection

build:
	docker build -t $(IMAGE_NAME) .

up: build
	docker run -itd --name $(CONTAINER_NAME) \
		-v $(TARGET_DIR):/root/infection \
		$(IMAGE_NAME)

run:
	docker exec -it $(CONTAINER_NAME) bash

clean:
	-docker stop $(CONTAINER_NAME)
	-docker rm $(CONTAINER_NAME)

fclean: clean
	-docker rmi $(IMAGE_NAME)
	-rm -f host_key.txt
	-rm -rf $(TARGET_DIR)

.PHONY: build up run clean fclean