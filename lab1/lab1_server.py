import socket

INTERFACE, SPORT = 'localhost', 8080
CHUNK = 100


##################################
# TODO: Implement me for Part 1! #
##################################
def send_intro_message(conn):
    # TODO: Replace {ONID} with your ONID (mine is lyakhovs)
    #       and {MAJOR} with your major (i.e. CS, ECE, any others?)
    intro_message = "Hello! Welcome to my ({ONID}) server! I'm majoring in {MAJOR}\n"

    # TODO: Send this intro message to the client. Don't forget to encode() it!
    #       hint: use the `conn` handle and `sendall`!


##################################
# TODO: Implement me for Part 2! #
##################################
def receive_long_message(conn):
    # First we receive the length of the message: this should be 8 total hexadecimal digits!
    # Note: `socket.MSG_WAITALL` is just to make sure the data is received in this case.
    data_length_hex = conn.recv(8, socket.MSG_WAITALL)

    # Then we convert it from hex to integer format that we can work with
    data_length = int(data_length_hex, 16)

    data = b""
    full_data = b""
    bytes_received = 0

    # TODO: Receive all data
    #      1. Keep going until `bytes_received` is less than `data_length` (hint: use a loop)
    #      2. Receive a `CHUNK` of data (see `CHUNK` variable above)
    #      3. Update `bytes_received` and `full_data` variables

    return full_data.decode()


def main():

    # Configure a socket object to use IPv4 and TCP
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        # Set interface and port
        server_socket.bind((INTERFACE, int(SPORT)))

        # Start listening for client connections (allow up to 5 connections to queue up)
        server_socket.listen(5)
        while True:

            # Accept a connection from a client
            conn, (client_host, client_port) = server_socket.accept()
            print("Connection received from:", client_host, "on port", client_port)

            """
            Part 1: Introduction
            """
            # TODO: Send the introduction message by implementing `send_intro_message` above.
            send_intro_message(conn)

            """
            Part 2: Long Message Exchange Protocol
            """
            # TODO: Receive long message by implementing the function above
            message = receive_long_message(conn)

            # TODO: print the received `message` to the screen!

# Run the `main()` function
if __name__ == "__main__":
    main()
