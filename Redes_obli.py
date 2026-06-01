#Leer entrada estándar, separar Destino del Mesanje #
import socket
import sys

# Lee los argumentos
port = int(sys.argv[1])

# Crea el socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

usuario = "fede" #la idea es que se cambie por el usuario que se autentique!!!

ip_emisor = socket.gethostbyname(socket.gethostname())  

# Loop que lee stdin
while True:
    linea = input()
    partes = linea.split(" ", 1)
    destino = partes[0]
    mensaje = partes[1]

    # Resolver ip
    if destino == "*":                      # Se fija si es brodcast
        ip = "255.255.255.255"
    else:
        ip = socket.gethostbyname(destino)

    formato_del_mensaje = f"{ip_emisor} {usuario} dice: {mensaje}" #seteo el tipo de mensaje

    # Enviar mensaje
    sock.sendto(formato_del_mensaje.encode(), (ip, port))
        
