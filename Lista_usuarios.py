from usuarios import *
import usuarios

lista_usuarios  = []
def agregar_usuario(usuario, nombre_completo):
    if len(lista_usuarios) > 0:
        for u in lista_usuarios:
            if u.get_usuario() == usuario:
                print(f"Error: El usuario '{usuario}' ya existe.")
                return False
    else:
        nuevo_usuario = usuarios.Usuario(usuario, nombre_completo)
        nuevo_usuario.set_contrasenia(input("Ingrese una contraseña para el usuario: "))
        lista_usuarios.append(nuevo_usuario)
        print(f"Usuario '{usuario}' agregado exitosamente.")
        return True

def eliminar_usuario(usuario):
    for u in lista_usuarios:
        if u.get_usuario() == usuario.get_usuario():
            lista_usuarios.remove(u)
            print(f"Usuario '{usuario.get_usuario()}' eliminado exitosamente.")
            return True
    print(f"Error: El usuario '{usuario.get_usuario()}' no existe.")
    return False

def mostrar_usuarios():
    if not lista_usuarios:
        print("No hay usuarios registrados.")
    else:
        print("Lista de usuarios:")
        for usuario in lista_usuarios:
            print(usuario)


def buscar_usuario(usuario):
    for u in lista_usuarios:
        if u.get_usuario() == usuario:
            return u
    return None