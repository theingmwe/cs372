import os
os.chdir('myfiles')

import asyncio

INTERFACE, SPORT = 'localhost', 8080
MAX_ATTEMPTS = 3


async def handle_client(reader, writer):
    password = "password123"  # Set the expected password here
    attempts = 0

    # Send password prompt
    await send_message(writer, "Please enter the password: ")

    while attempts < MAX_ATTEMPTS:
        # Receive password from the client
        received_password = await receive_message(reader)

        # Check if the password is correct
        if received_password == password:
            await send_message(writer, "Login Successful!")
            break
        else:
            attempts += 1
            if attempts < MAX_ATTEMPTS:
                await send_message(writer, f"Invalid password. Please try again ({MAX_ATTEMPTS - attempts} attempt(s) remaining): ")
            else:
                await send_message(writer, "Maximum attempts reached. Closing the connection.")
                break

    # Continue with FTP functionality if the login is successful
    if attempts < MAX_ATTEMPTS:
        await send_message(writer, "Welcome to the FTP server!")

        while True:
            # Receive command from the client
            command = await receive_message(reader)

            # Process the command
            if command == "list":
                cwd = os.getcwd()  # Get the current working directory (cwd)
                files = os.listdir(cwd)  # Get all the files in that directory
                # print("Files in %r: %s" % (cwd, files))
                file_list = "\n".join(files)
                await send_message(writer, "ACK")
                await send_message(writer, file_list)
                
            elif command.startswith("put"):
                _, filename = command.split(" ")
                await receive_file(reader, filename)
                await send_message(writer, f"File '{filename}' uploaded successfully.")
            elif command.startswith("get"):
                _, filename = command.split(" ")
                await send_file(writer, filename)
            elif command.startswith("remove"):
                _, filename = command.split(" ")
                try:
                    os.remove(os.path.join("myfiles", filename))
                    await send_message(writer, f"File '{filename}' removed successfully.")
                except FileNotFoundError:
                    await send_message(writer, f"File '{filename}' not found.")
            elif command == "close":
                break
            else:
                await send_message(writer, f"Invalid command: {command}")

    writer.close()
    await writer.wait_closed()


async def receive_message(reader):
    # First we receive the length of the message: this should be 8 total hexadecimal digits!
    data_length_hex = await reader.readexactly(8)
    data_length = int(data_length_hex.decode(), 16)  # Decode the received data before conversion

    full_data = await reader.readexactly(data_length)
    return full_data.decode()


async def send_message(writer, message):
    data_length_hex = hex(len(message))[2:].zfill(8)
    writer.write(data_length_hex.encode())
    writer.write(message.encode())
    await writer.drain()


# async def receive_file(reader, filename):
#     file_path = os.path.join("myfiles", filename)
#     with open(file_path, "wb") as file:
#         # Receive the file data in chunks and write to the file
#         while True:
#             data_chunk = await receive_message(reader)
#             if not data_chunk:
#                 break
#             file.write(data_chunk.encode())

async def receive_file(reader, filename):
    file = open(filename, "w")
    file_contents = await receive_message(reader)
    file.write(file_contents)
    file.close()

async def send_file(writer, filename):
    file_path = os.path.join("myfiles", filename)
    try:
        with open(file_path, "rb") as file:
            file_data = file.read()
            await send_message(writer, file_data)
    except FileNotFoundError:
        await send_message(writer, f"File '{filename}' not found.")


async def main():
    server = await asyncio.start_server(handle_client, INTERFACE, SPORT)

    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')

    async with server:
        await server.serve_forever()


# Run the `main()` function
if __name__ == "__main__":
    asyncio.run(main())
