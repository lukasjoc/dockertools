import docker
from datetime import timedelta, datetime
from tabulate import tabulate

def container_info(client):
    container_data = []
    for container in client.containers.list():
        attrs = container.attrs
        def get_container_created():
            pattern = '%Y-%m-%dT%H:%M:%S'
            today_time = datetime.strptime(datetime.strftime(datetime.today(), pattern), pattern)
            create_time = datetime.strptime(attrs["Created"].split(".")[0], pattern)
            created = abs(today_time - create_time)
            if created.days >= 1:
                return f"{created.days} days ago"
            return str(timedelta(seconds=int(created.total_seconds())-3600))

        def get_container_ports():
            ports = attrs["NetworkSettings"]["Ports"]
            formatted_ports = ""
            hosted = []
            for port, mapping in ports.items():
                if mapping != None:
                    for item in mapping:
                        formatted_ports += f"{item['HostIp']}:{item['HostPort']}->{port}\xa0"
                else:
                    formatted_ports += f"{port}\xa0"
            return formatted_ports

        def get_container_ip():
            net_id = attrs["NetworkSettings"]["IPAddress"]
            if net_id != "":
                return net_id
            if attrs["HostConfig"]["NetworkMode"] != "default":
                network_name = attrs["HostConfig"]["NetworkMode"]
                return attrs["NetworkSettings"]["Networks"][network_name]["IPAddress"]

        container_data.append([
            attrs["Config"]["Hostname"],
            attrs["Config"]["Image"],
            get_container_created(),
            attrs["State"]["Status"],
            get_container_ports(),
            attrs["Name"][1:],
            get_container_ip()
        ])

    container_cols = [ "CONTAINER ID", "IMAGE", "CREATED", "STATUS", "PORTS", "NAMES", "IP ADDRESS" ]
    return container_data, container_cols

if __name__ == "__main__":
    cl = docker.from_env(max_pool_size=15)
    data, cols = container_info(client=cl)
    print(tabulate(data, headers=cols))

