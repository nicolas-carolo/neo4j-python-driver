import socket
import neo4j
import json

drivers = {}
_id = 0

def next_id():
    global _id
    _id += 1
    return _id

def process_request(req):
    req = json.loads(req)
    name = req["name"]
    if name == "NewDriver":
        print("Got new driver request")
        data = req["data"]
        auth = data["authorizationToken"]["data"]
        auth = neo4j.AuthToken(
            scheme=auth["scheme"],
            principal=auth["principal"],
            credentials=auth["credentials"],
            realm=auth["realm"],
            ticket=auth["ticket"])
        driver = neo4j.GraphDatabase.driver(data["uri"], auth=auth)
        driver_id = next_id()
        drivers[driver_id] = driver

        response = {"name": "Driver", "data": {"id": "%s" % driver_id }}
        print(response)
        response = json.dumps(response)
        return response

    else:
        raise Exception("Unknown request")


if __name__ == "__main__":

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("", 9876))
    server_socket.listen()
    while True:
        client_socket, _ = server_socket.accept()
        print("Got a client")

        writer = client_socket.makefile(mode='w', encoding='utf-8')
        reader = client_socket.makefile(mode='r', encoding='utf-8')

        # Read one line
        in_request = False
        request = ""

        while True:
            line = reader.readline().strip()
            if line == "#request begin":
                print("Start of request")
                in_request = True
            elif line == "#request end":
                print("End of request")
                in_request = False
            elif line and in_request:
                request += line

            if request and not in_request:
                response = process_request(request)
                writer.write("#response begin\n")
                writer.write(response+"\n")
                writer.write("#response end\n")
                writer.flush()

                request = ""

