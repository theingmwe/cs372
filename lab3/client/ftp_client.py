import os
os.chdir('myfiles')

import asyncio

INTERFACE, SPORT = 'localhost', 8080

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


async def list_files():
    cwd = os.getcwd()  # Get the current working directory (cwd)
    files = os.listdir(cwd)  # Get all the files in that directory    
    return "\n".join(files)


async def put_file(filename):
    try:
        with open(f"myfiles/{filename}", 'rb') as file:
            content = file.read()
            return content
    except FileNotFoundError:
        return None


async def get_file(filename, content):
    if content:
        try:
            with open(f"myfiles/{filename}", 'wb') as file:
                file.write(content)
                return True
        except:
            return False
    else:
        return False


async def remove_file(filename):
    try:
        os.remove(f"myfiles/{filename}")
        return True
    except FileNotFoundError:
        return False


async def main():
    reader, writer = await asyncio.open_connection(INTERFACE, SPORT)

    # Receive password prompt
    password_prompt = await receive_message(reader)
    print(password_prompt)

    while True:
        # Enter password
        password = input("> ")
        await send_message(writer, password)

        # Receive response
        response = await receive_message(reader)
        print(response)

        # Check if login is successful
        if response == "Login Successful!":
            break

    command_prompt = await receive_message(reader)
    print(command_prompt)

    # Continue with FTP functionality
    while True:
        # Receive command prompt
        
        # Enter command
        command = input("> ")

        await send_message(writer, command)

        # Receive command response
        response = await receive_message(reader)
        # print(response)

        # Process command
        if command == "list":
            if response == "ACK":
                response = await receive_message(reader)
                print(response)

                # file_list = await list_files()
                # await send_message(writer, file_list)
                # print(file_list)
            else:
                print("Error: ", response)
        elif command.startswith("put"):
            if response == "ACK":
                filename = command.split()[1]
                content = await put_file(filename)
                if content:
                    await send_message(writer, "ACK")
                    await send_message(writer, content)
                else:
                    await send_message(writer, "NAK File not found")
            else:
                print("Error:", response)
        elif command.startswith("get"):
            if response == "ACK":
                filename = command.split()[1]
                await send_message(writer, "ACK")
                content = await receive_message(reader)
                success = await get_file(filename, content)
                if success:
                    print("File downloaded successfully.")
                else:
                    print("Error: File not found on the server.")
            else:
                print("Error:", response)
        elif command.startswith("remove"):
            if response == "ACK":
                filename = command.split()[1]
                success = await remove_file(filename)
                if success:
                    print("File removed successfully.")
                    await send_message(writer, "ACK")
                else:
                    await send_message(writer, "NAK File not found")
            else:
                print("Error:", response)
        elif command == "close":
            if response == "ACK":
                writer.close()
                await writer.wait_closed()
                break
            else:
                print("Error:", response)
        else:
            print("Invalid command.")

    print("Connection closed.")


# Run the `main()` function
if __name__ == "__main__":
    asyncio.run(main())