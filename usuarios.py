
import sys
from Lista_usuarios import *


class Usuario :
    def __init__(self, usuario=None, nombre_completo=None  , contrasenia = None, habilitado = False):
        self.usuario = usuario
        self.nombre_completo = nombre_completo
        self.contrasenia = contrasenia
        self.habilitado = habilitado
    def get_usuario(self):
        return self.usuario
    
    def get_nombre_completo(self):
        return self.nombre_completo 
    
    def get_contrasenia(self):
        return self.contrasenia
    
    def set_usuario(self, usuario):
        self.usuario = usuario
    
    def set_nombre_completo(self, nombre_completo):
        self.nombre_completo = nombre_completo
    
    def set_contrasenia(self, contrasenia):
        self.contrasenia = contrasenia
    
    def __str__(self):
        return f"Usuario: {self.usuario}, Nombre Completo: {self.nombre_completo}"
    
    def __autenticar__ (self, contrasenia):
        return self.contrasenia == contrasenia  
    
    def __validar_usuario__(self, usuario):
        print("Ingrese su contraseña:")
        contrasenia = input()
        if self.__autenticar__(contrasenia):
            self.habilitado = True
            print(f"Bienvenido {self.get_nombre_completo()}!")
        else:
            print("Contraseña incorrecta. Por favor, intente nuevamente.")  