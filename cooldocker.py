import docker
from tabulate import tabulate
from datetime import datetime

def container_info(client):
    container_data = []
    container_cols = [ "CONTAINER ID", "IMAGE", "CREATED", "STATUS", "PORTS", "NAMES", "IP ADDRESS" ]
    for container in client.containers.list():
        attrs = container.attrs

        def get_container():
            return attrs["Config"]["Hostname"]

        def get_container_image():
            return attrs["Config"]["Image"]

        # Fuck Timezones
        def get_container_created():
            today_time = datetime.strptime(datetime.strftime(datetime.today(), '%Y-%m-%dT%H:%M:%S'), "%Y-%m-%dT%H:%M:%S")
            create_time = datetime.strptime(attrs["Created"].split(".")[0], "%Y-%m-%dT%H:%M:%S")
            created = abs(today_time - create_time)
            # if created.days >= 1:
            #     return f"{created.days} days ago"
            return created

        # TODO: Calculate status time if up
        # from ["State"]["StartedAt"], ["State"]["FinishedAt"]
        def get_container_status():
            return attrs["State"]["Status"]

        # TODO: fix port to be HOSTIP:HOSTPORT->EXPOSED
        def get_container_ports():
            ports = attrs["NetworkSettings"]["Ports"]
            hosted = []
            for mappings in ports.values():
                if mappings != None:
                    for mapping in mappings:
                        hosted.append(f"{mapping['HostIp']}:{mapping['HostPort']}")

            formatted_ports = ""
            for hos in hosted:
                formatted_ports += f"{hos}\xa0"
            for exp in ports.keys():
                formatted_ports += f"{exp}\xa0"
            return formatted_ports

        def get_container_name():
            return attrs["Name"][1:]

        def get_container_ip():
            net_id = attrs["NetworkSettings"]["IPAddress"]
            if net_id != "":
                return net_id
            if attrs["HostConfig"]["NetworkMode"] != "default":
                network_name = attrs["HostConfig"]["NetworkMode"]
                return attrs["NetworkSettings"]["Networks"][network_name]["IPAddress"]

        container_data.append([
            get_container(),
            get_container_image(),
            get_container_created(),
            get_container_status(),
            get_container_ports(),
            get_container_name(),
            get_container_ip()
        ])

    return container_data, container_cols

if __name__ == "__main__":
    cl = docker.from_env(max_pool_size=10)

    data, cols = container_info(client=cl)
    print(tabulate(data, headers=cols))

