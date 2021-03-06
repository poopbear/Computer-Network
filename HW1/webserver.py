from socket import *
import os
import mimetypes


class SimpleServer:

    def __init__(self, port, host_addr):
        self.__socket = None
        self.__conn_socket = None
        self.__port = port
        self.__host_addr = host_addr

    # initialize socket
    def init_socket(self):
        self.__socket = socket(AF_INET, SOCK_STREAM)
        self.__socket.bind((self.__host_addr, self.__port))
        self.__socket.listen(10)
        print("TCP Server is ready for port number {}.\n".format(self.__port))

    # accept and handle client's request
    def serve_request(self):
        while True:
            self.__conn_socket, _ = self.__socket.accept()
            request = self.__conn_socket.recv(1024).decode()

            # parse file name from the request
            file_name = request.split(" ", 2)
            if len(file_name) > 1:
                file_name = file_name[1]
                if file_name == "/":
                    file_name = "index.html"
                else:
                    file_name = file_name[1:]
                print("File requested: {}".format(file_name))

                # open and get the file content
                file, status_code = self.load_file(file_name)
                print("Status: {}".format(status_code))

                # send header and the file content
                self.__conn_socket.send(self.get_header(file_name, status_code).encode())
                if status_code == 200:
                    self.__conn_socket.send(file.read())
                else:
                    self.__conn_socket.send("404 Not Found".encode())

            # finish the request with closing socket
            self.__conn_socket.close()
            print("Request process ended.\n")

    # load the file and return
    def load_file(self, file_name):
        try:
            file = open(file_name, "rb")
            return file, 200
        except FileNotFoundError:
            return None, 404

    # return header string
    def get_header(self, file_name, status_code):
        try:
            file_size = os.path.getsize(file_name)
        except FileNotFoundError:
            file_size = len("404 Not Found")
        _, file_ext = os.path.splitext(file_name)
        print("Content-Type: {}".format(self.get_file_type(file_ext, status_code)))
        print("Content-Length: {} bytes".format(file_size))
        return "\r\n".join([
            "HTTP/1.1 {} {}".format(status_code, self.get_status_str(status_code)),
            "Content-Type: {}".format(self.get_file_type(file_ext, status_code)),
            "Content-Length: {}".format(file_size)
        ]) + "\r\n\r\n"

    # return status string
    def get_status_str(self, status_code):
        if status_code == 200:
            return "OK"
        else:
            return "Not Found"

    def get_file_type(self, file_ext, status_code):
        if status_code == 200:
            return mimetypes.types_map.get(file_ext, "application/octet-stream")
        else:
            return "text/plain"


if __name__ == "__main__":
    server = SimpleServer(10080, "")
    server.init_socket()
    server.serve_request()
