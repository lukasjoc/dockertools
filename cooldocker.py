import docker

if __name__ == "__main__":
    cl = docker.from_env()

    # CONTAINER ID, IMAGE, COMMAND, CREATED, STATUS, PORTS, NAME, IP ADDRESS
    containers = cl.containers.list()
    container_ids = [l.id for l in containers]
    for container_id in container_ids:
        container = cl.containers.get(container_id)
        a = container.attrs["Config"]
        print(a)

    # TODO: REPOSITORY, TAG, IMAGE ID, CREATED, SIZE
    images = cl.images.list()
    image_ids = [l.id for l in images]
    for image_id in image_ids:
        image = cl.images.get(image_id)
        a = image.attrs["Config"]
        print(a)

    #  TODO: add volumes and networks too

