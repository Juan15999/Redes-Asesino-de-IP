import socket
import sys

# Lee los argumentos
port = int(sys.argv[1])

# Crea el socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

usuario = "user"                            # La idea es que se cambie por el usuario que se autentique

ip_emisor = socket.gethostbyname(socket.gethostname())  

while True:
    linea = input()
    partes = linea.split(" ", 1)
    destino = partes[0]
    if len(partes) < 2:                     # Se fija si hay 2 argumentos, sino lo vuelve a pedir
        print("Formato invalido, tiene que ser |Destino| |Mensaje|")
        continue
    mensaje = partes[1]
    
    # resolver ip
    if destino == "*":                      # Se fija si es brodcast
        ip = "255.255.255.255"
    else:
        ip = socket.gethostbyname(destino)

    if mensaje.startswith("&file"):
        path = mensaje.split(" ", 1)[1]     # Te da solo el ./
        try:         
            with open(path, "rb") as f:
                datos = f.read()
            
            nombre_archivo = path.split("/")[-1]    # Extrae el formato del archivo 
            encabezado = f"{ip_emisor} {usuario} &file {nombre_archivo}".encode()
            sock.sendto(encabezado, (ip, port))
            sock.sendto(datos, (ip, port))          # devulve archivo
        except FileNotFoundError:
            print(f"Error: no se encontró el archivo {path}")

    else:
        formato_del_mensaje = f"{ip_emisor} {usuario} dice: {mensaje}"      # Seteo el tipo de mensaje 
        sock.sendto(formato_del_mensaje.encode(), (ip, port))               # Devuelve mensaje
