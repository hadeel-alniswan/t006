import socket  # Import the socket module to create the server and handle connections
import os  # Import the os module to handle file paths

# Define constants for the server
HOST = 'localhost'  # The host where the server will run (localhost means your local machine)
PORT = 5698  # The port number where the server will listen for requests
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Get the base directory of this script to find HTML files

# Start the server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a socket for IPv4 and TCP
server_socket.bind((HOST, PORT))  # Bind the socket to the specified host and port
server_socket.listen(5)  # Listen for incoming connections (maximum 5 connections at once)
print(f"Server running on http://{HOST}:{PORT}/")  # Print to the terminal that the server is running

while True:  # Run the server continuously to accept multiple connections
    # Accept client connections
    client_socket, client_address = server_socket.accept()  # Accept a connection and get the client's socket and address
    request = client_socket.recv(1024).decode()  # Receive the HTTP request (up to 1024 bytes) and decode it

    # Print the request details
    print(f"Request received from {client_address}:\n{request}")  # Print the request and client address to the terminal

    if not request:  # If there's no request, close the connection and continue to the next one
        client_socket.close()
        continue

    # Split the request into lines and parse the first line
    request_line = request.splitlines()[0]  # Get the first line of the HTTP request
    try:
        method, path, _ = request_line.split()  # Split the line into method (GET), path (URL), and HTTP version
    except ValueError:
        client_socket.close()  # If the request is malformed, close the connection
        continue

    # Default response: main_en.html
    if path in ["/", "/en", "/index.html", "/main_en.html"]:  # If the request is for the English homepage
        try:
            # Try to open the main_en.html file and send its content to the client
            with open(os.path.join(BASE_DIR, "main_en.html"), 'rb') as f:
                content = f.read()  # Read the content of the file
            response = f"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n".encode() + content  # Prepare the response
        except FileNotFoundError:  # If the file is not found, send a 404 error
            response = f"HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\n\r\nError: File not found".encode()

    # Arabic page response: main_ar.html
    elif path in ["/ar", "/main_ar.html"]:  # If the request is for the Arabic homepage
        try:
            with open(os.path.join(BASE_DIR, "main_ar.html"), 'rb') as f:
                content = f.read()  # Read the content of the Arabic page
            response = f"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n".encode() + content  # Send the content
        except FileNotFoundError:  # If the file is not found, send a 404 error
            response = f"HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\n\r\nError: File not found".encode()

    # Supporting material page: supporting_material_en.html
    elif path == "/supporting_material_en.html":  # If the request is for the supporting material page
        try:
            with open(os.path.join(BASE_DIR, "supporting_material_en.html"), 'rb') as f:
                content = f.read()  # Read the content of the supporting material page
            response = f"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n".encode() + content  # Send the content
        except FileNotFoundError:  # If the file is not found, send a 404 error
            response = f"HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\n\r\nError: File not found".encode()

    # Handle form requests and redirect based on file type (image/video)
    elif path.startswith("/support_request"):  # If the request is for the supporting file request
        query = path.split("?")[1] if "?" in path else ""  # Extract the query part from the URL (e.g., ?file=xxx)
        file_request = query.split("=")[-1]  # Get the requested file from the query string

        # Determine if the requested file is an image or video based on its extension
        if file_request.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp")):  # Check for image types
            redirect_url = f"https://www.google.com/search?q={file_request}&tbm=isch"  # Redirect to Google Images
            response = f"HTTP/1.1 307 Temporary Redirect\r\nLocation: {redirect_url}\r\n\r\n".encode()

        elif file_request.lower().endswith((".mp4", ".avi", ".mkv", ".mov", ".flv")):  # Check for video types
            redirect_url = f"https://www.youtube.com/results?search_query={file_request}"  # Redirect to YouTube search
            response = f"HTTP/1.1 307 Temporary Redirect\r\nLocation: {redirect_url}\r\n\r\n".encode()

        else:  # If the file type is not recognized (neither image nor video)
            response = f"HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\n\r\nError: File type not recognized".encode()

    # Handle invalid paths (404)
    else:  # If the request is for an invalid or nonexistent path
        response = f"HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\n\r\nError: File not found".encode()

    # Send the response to the client
    client_socket.sendall(response)  # Send the response content to the client
    client_socket.close()  # Close the client socket after sending the response
