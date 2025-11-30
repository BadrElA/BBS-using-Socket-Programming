import socket
import threading
import json

# This module provides functionality for:
#   Connecting to the server
#   Joining and leaving groups
#   Posting messages to groups
#   Retrieving group information, such as members and messages

# Function to handle receiving messages from the server
def receive_messages(sock):
	while True:
		try:
			# Receive message from server
			message = sock.recv(1024).decode('utf-8')
			if not message:
				# Handle server disconnection
				print("server disconnected")
				break
			else:
				print("\r" + message + "\n> ", end="")
		except:
			# Handle any exceptions (e.g., connection errors)
			break

# Main function to run the client
# Every request sent to the server is formatted as a JSON object:
# {
#     "command": <command_name>,
#     <additional fields depending on command>: <value>
# }
#
# Supported Commands:
#
#   %connect <host> <port>
#       - Establishes a TCP connection to the server at the specified host and port.
#
#   %join
#       - Joins the default group ("default").
#
#   %post ; <subject> ; <message>
#       - Posts a message with a subject and body to the default group.
#
#   %users
#       - Requests the list of all users currently in the default group.
#
#   %leave
#       - Leaves the default group.
#
#   %message <message_id>
#       - Retrieves and displays a specific message (by ID) from the default group.
#
#   %exit
#       - Disconnects from the server and terminates the client program.
#
#   %groups
#       - Requests the list of all available groups on the server.
#
#   %groupjoin <group_name>
#       - Joins the specified group.
#
#   %grouppost ; <groupname> ; <subject> ; <message>
#       - Posts a message with subject and body to the specified group.
#
#   %groupusers <group_name>
#       - Requests the list of users in the specified group.
#
#   %groupleave <group_name>
#       - Leaves the specified group.
#
#   %groupmessage <group_name> <message_id>
#       - Retrieves a specific message (by ID) from the specified group.
#
def run():
	client_socket = None # socket object for client-server communication
	name_sent = False # track if the username has been sent to the server
	while True:
		# user input
		command = input("> ")
		command_args = command.split()

		# no command entered
		# this should never really happen since the user has to type something to hit enter
		if not command_args:
			print("no valid command found")
			continue

		# Handle the %connect command (establishes connection to server)
		elif command_args[0] == "%connect":
			if len(command_args) != 3:
				print("usage: %connect <host> <port>")
				continue
			HOST, PORT = str(command_args[1]), int(command_args[2])
			# establish connection to server and start receiving thread
			# if connection fails, print error message and continue the loop to allow user to try again
			try:
				client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				client_socket.connect((HOST, PORT))
				print(f"connected to {HOST} on port {PORT}")
				recieve_thread = threading.Thread(target=receive_messages, args=(client_socket,))
				recieve_thread.start()
			except:
				print("could not connect to server")

		# Command to join the default group
		elif command_args[0] == "%join":
			if len(command_args) != 1:
				print("usage: %join")
				continue
			request = {"command": "%groupjoin", "group": "default"}
			client_socket.sendall(json.dumps(request).encode('utf-8'))

		# Command to post a message to the default group
		elif command_args[0] == "%post":
			post_command_args = command.split(";")
			if len(post_command_args) != 3:
				print("usage: %post ; subject ; <message>")
				continue
			request = {"command": "%grouppost", "group": "default", "subject": post_command_args[1].strip(), "message": post_command_args[2].strip()}
			client_socket.sendall(json.dumps(request).encode('utf-8'))

		# Command to list users in the default group
		elif command_args[0] == "%users":
			if len(command_args) != 1:
				print("usage: %users")
				continue
			request = {"command": "%groupusers", "group": "default"}
			client_socket.sendall(json.dumps(request).encode('utf-8'))

		# Command to leave the default group
		elif command_args[0] == "%leave":
			if len(command_args) != 1:
				print("usage: %leave")
				continue
			request = {"command": "%groupleave", "group": "default"}
			client_socket.sendall(json.dumps(request).encode('utf-8'))

		# Command to get a specific message from the default group
		elif command_args[0] == "%message":
			if len(command_args) != 2:
				print("usage: %message <message_id>")
				continue
			request = {"command": "%groupmessage", "group": "default", "message_id": int(command_args[1].strip())}
			client_socket.sendall(json.dumps(request).encode('utf-8'))

		# Command to exit the client
		elif command_args[0] == "%exit":
			request = {"command": "%exit"}
			client_socket.sendall(json.dumps(request).encode('utf-8'))
			client_socket.close()
			break

		# Command to list all available groups on the server
		elif command_args[0] == "%groups":
			request = {"command": "%groups"}
			client_socket.sendall(json.dumps(request).encode('utf-8'))
		
		# Command to join a specific group
		elif command_args[0] == "%groupjoin":
			if len(command_args) != 2:
				print("usage: %groupjoin <group_name>")
				continue
			request = {"command": "%groupjoin", "group": command_args[1]}
			client_socket.sendall(json.dumps(request).encode('utf-8'))
		
		# Command to post a message to a specific group
		elif command_args[0] == "%grouppost":
			post_command_args = command.split(";")
			if len(post_command_args) != 4:
				print("usage: %grouppost ; <groupname> ; <subject> ; <message>")
				continue
			request = {"command": "%grouppost", "group": post_command_args[1].strip(), "subject": post_command_args[2].strip(), "message": post_command_args[3].strip()}
			client_socket.sendall(json.dumps(request).encode('utf-8'))

		# Command to list users in a specific group
		elif command_args[0] == "%groupusers":
			if len(command_args) != 2:
				print("usage: %groupusers <group_name>")
				continue
			request = {"command": "%groupusers", "group": command_args[1]}
			client_socket.sendall(json.dumps(request).encode('utf-8'))
		
		# Command to leave a specific group
		elif command_args[0] == "%groupleave":
			if len(command_args) != 2:
				print("usage: %groupleave <group_name>")
				continue
			request = {"command": "%groupleave", "group": command_args[1]}
			client_socket.sendall(json.dumps(request).encode('utf-8'))
		
		# Command to get a specific message from a specific group
		elif command_args[0] == "%groupmessage":
			if len(command_args) != 3:
				print("usage: %groupmessage <group_name> <message_id>")
				continue
			request = {"command": "%groupmessage", "group": command_args[1], "message_id": int(command_args[2])}
			client_socket.sendall(json.dumps(request).encode('utf-8'))
		
		# Handling unknown commands
		elif command_args[0] and name_sent:
			print("command not found")
			continue

		else:
			# Sending username to server
			client_socket.sendall(command.encode('utf-8'))
			name_sent = True # set flag to true after sending username



if __name__ == "__main__":
	run()