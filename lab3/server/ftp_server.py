import os
os.chdir('myfiles')

import socket
import asyncio

INTERFACE, SPORT = 'localhost', 8080
CHUNK = 100
PASSWORD = "password1"
password_attempt = 0

async def send_password_prompt(writer):
    # When the client makes a connection to the server, the server should prompt it to enter a password.
    # This password should be set ahead of time on the server.
    password_message = "Please enter the password: "

    writer.write(password_message.encode())
    await writer.drain()


async def send_intro_message(writer):
    intro_message = "Hello! Welcome to my (oot, oommenr, campbel2) server! I'm majoring in CS\n"

    writer.write(intro_message.encode())
    await writer.drain()

    
async def receive_long_message(reader: asyncio.StreamReader):
    # First we receive the length of the message: this should be 8 total hexadecimal digits!
    # Note: `socket.MSG_WAITALL` is just to make sure the data is received in this case.
    data_length_hex = await reader.readexactly(8)

    # Then we convert it from hex to integer format that we can work with
    data_length = int(data_length_hex, 16)

    full_data = await reader.readexactly(data_length)
    return full_data.decode()


async def handle_client(reader, writer):
    #prompt user for password
    await send_password_prompt(writer)

    # receive password
    message = await receive_long_message(reader)
    writer.close()
    await writer.wait_closed()

    #check if password is correct or not
    if message.strip() == PASSWORD:
        #if correct, continue as lab2
        print("Login Successful!")

        await send_intro_message(writer)
        message = await receive_long_message(reader)

        print("done: " +  message[-8:])

        writer.close()
        await writer.wait_closed()

    else:
        password_attempt += 1
        
        #TODO: if password_attempt = 3, implement error handling


async def main():
    server = await asyncio.start_server(
            handle_client,
            INTERFACE, SPORT
    )

    async with server:
        await server.serve_forever()

# Run the `main()` function
if __name__ == "__main__":
    asyncio.run(main())
