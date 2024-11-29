import socket  #a socket module to create the server and handle connections
import os  #to handle file paths
import base64


HOST = '192.168.68.109' #local network ip
PORT = 5698  #port number
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) #get the base directory of this script to find HTML files


CONTENT_TYPES = {
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.gif': 'image/gif',
    '.mp4': 'video/mp4',
}

# Start the server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # creates a socket for IPv4 and TCP
server_socket.bind((HOST, PORT)) 
server_socket.listen(5)  #max 5 connections at once
print(f"Server running on http://{HOST}:{PORT}/")  # prints to the terminal that the server is running

while True: 
    # Accept client connections
    client_socket, client_address = server_socket.accept()  # accepts a connection and gets the client's socket & address
    request = client_socket.recv(1024).decode()  # Receive the HTTP request (up to 1024 bytes) and decode it

    
    print(f"Request received from {client_address}:\n{request}") 

    if not request:  # when there's no request, close the connection and continue to the next one
        client_socket.close()
        continue

   
    request_line = request.splitlines()[0]  #get the first line of the HTTP request
    try:
        method, path, _ = request_line.split()  # splits line into method (GET), path (URL), and HTTP version
    except ValueError:
        client_socket.close() 
        continue

    # main_en.html
    if path in ["/", "/en", "/index.html", "/main_en.html"]:  # request is for the English homepage
        try:
            with open(os.path.join(BASE_DIR, "main_en.html"), 'rb') as f: #rb is read binary mode
                content = f.read()  
            response = f"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n".encode() + content  
        except FileNotFoundError: 
            response = f"HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\n\r\nError: File not found".encode()

    # main_ar.html
    elif path in ["/ar", "/main_ar.html"]:  #request is for the Arabic homepage
        try:
            with open(os.path.join(BASE_DIR, "main_ar.html"), 'rb') as f:
                content = f.read() 
            response = f"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n".encode() + content  
        except FileNotFoundError:  
            response = f"HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\n\r\nError: File not found".encode()

    # supporting_material_en.html
    elif path == "/supporting_material_en.html":  #request is for the supporting material page
        try:
            with open(os.path.join(BASE_DIR, "supporting_material_en.html"), 'rb') as f:
                content = f.read()  
            response = f"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n".encode() + content 
        except FileNotFoundError: 
            response = f"HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\n\r\nError: File not found".encode()

    # supporting_material_ar.html
    elif path == "/supporting_material_ar.html":  #request is for the supporting material page
        try:
            with open(os.path.join(BASE_DIR, "supporting_material_ar.html"), 'rb') as f:
                content = f.read()  
            response = f"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n".encode() + content  
        except FileNotFoundError:  
            response = f"HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\n\r\nError: File not found".encode()

    # assets folder (css, img, etc.)
    elif path.startswith("/assets/"):  #request is for a file inside the assets folder
        asset_path = os.path.join(BASE_DIR, path.lstrip("/"))  # removes the slash and creates the full path to the file

        if os.path.exists(asset_path):  
           
            file_extension = os.path.splitext(asset_path)[1].lower()
            content_type = CONTENT_TYPES.get(file_extension, 'application/octet-stream')  

           
            with open(asset_path, 'rb') as f:
                content = f.read()

            response = f"HTTP/1.1 200 OK\r\nContent-Type: {content_type}\r\n\r\n".encode() + content  
        else:
            response = f"HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\n\r\nError: File not found".encode()

    elif path.startswith("/support_request"):
        
        if "file=" in path:
            file_name = path.split("file=")[-1]  # gets the file name after 'file='
            file_path = os.path.join(BASE_DIR,"assets/img", file_name)  #full path to the file
            
            
            if os.path.exists(file_path):
                #content type based on the file extension
                if file_name.endswith(('.jpg', '.jpeg', '.png', '.gif')):
                    content_type = "image/*"
                elif file_name.endswith('.mp4'):
                    content_type = "video/mp4"
                else:
                    content_type = "application/octet-stream"

                
                with open(file_path, 'rb') as f:
                    content = f.read()
                encoded_content = base64.b64encode(content).decode('utf-8')

                # constructs the response HTML to display the image on the page 
                #the f takes the variable and puts the value in its place
                html_response = f""" 
                <html>
                <body>
                    <h1>Requested Image</h1>
                    <img src="data:{content_type};base64,{encoded_content}" width="400" height="300" />
                    <br><br>
                    <a href="/supporting_material_en.html">Go back to the page</a>
                </body>
                </html>
                """
                response = f"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n".encode() + html_response.encode()

            else:
                
                if file_name.endswith(('.jpg', '.jpeg', '.png', '.gif')):
                    redirect_url = f"https://www.google.com/search?q={file_name}&tbm=isch"
                elif file_name.endswith('.mp4'):
                    redirect_url = f"https://www.youtube.com/results?search_query={file_name}"
                else:
                    redirect_url = f"https://www.google.com/search?q={file_name}"

                
                response= f"HTTP/1.1 307 Temporary Redirect\r\nLocation: {redirect_url}\r\n\r\n".encode()
   

    
    else:  
        response = f"HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\n\r\nError: File not found".encode()

    # finally it sends the response to the client
    client_socket.sendall(response) 
    client_socket.close()  
