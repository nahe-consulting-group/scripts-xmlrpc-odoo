#!/usr/bin/python
# CUIDADO elegir bin del python correcto
# modificar la primer linea con which python.
# si está en un enviroment de pyhton usar la primer linea 
# Este script se testeo del 9 al 11 y anduvo. Tambien del 10 al 11 anduvo. Tambien anda desde odoo 8 a 11
import sys
import xmlrpc.client
import ssl

user_o = 'completar' #el usuario de odoo origen
user_d = 'completar' #el usuario de odoo destino
pwd_o = 'completar' # contrasenia de usuario odoo origen
pwd_d = 'completar' # contrasenia de usuario destino
dbname_o = 'completar'  # nombre de base de datos origen
dbname_d = 'completar' # nombre de base de datos destino
web_o = 'completar' # ip o dir web del origen
web_d = 'completar' # ip o dir web del destino
# datos de los modelos y campos
model_o = 'completar' # nombre del modelo de origen
model_d = 'completar' #nombre del modelo del destino
idant_o = 'completar' # nombre del campo a usar en el destino para almacenar id anterior, dejar vacio si no se usa
# Es necesario crear el campo x_id_anterior en el model_d para usarlo en la variable idant_o
condi1_o = [] # se labura con los padres  parent_id = False
# campos que quiero migrar del odoo origen
# campos a tener en cuenta casos especiales.
# company_type: puede tener dos valores [person,company] es importante usar para ('id', '>', '10')
#               primero se deben migrar todas las empresas is_company = true
#               segundo se deben migrar todas las personas is_company != true  (no se pone false)
# estos campos son para res.partner  hay que modificarlos para otos modelos o casos de uso. 
campos = ['id', 'name','symbol']

# esto genera el contexto para que se conecte
gcontext = ssl._create_unverified_context()

# Aqui se obtiene el uid_o de los datos de origen.
sock_common_o = xmlrpc.client.ServerProxy (('{}/xmlrpc/common'.format(web_o)),context=gcontext)
uid_o = sock_common_o.login(dbname_o, user_o, pwd_o)

# Aqui se obtiene el uid_d de los datos de destino.
sock_common_d = xmlrpc.client.ServerProxy (('{}/xmlrpc/common'.format(web_d)),context=gcontext)
uid_d = sock_common_d.login(dbname_d, user_d, pwd_d)

# Aqui se conecta con el objeto del origen
sock_o = xmlrpc.client.ServerProxy(('{}/xmlrpc/object'.format(web_o)),context=gcontext)

# Aqui se conecta con el objeto del destino
sock_d = xmlrpc.client.ServerProxy(('{}/xmlrpc/object'.format(web_d)),context=gcontext)

print("===========================================")
print("Se van a importar los siguientes registros:")
print("Web de origen..: ",web_o)
print("Modelo a migrar: ",model_o)
print("Condicion regis: ",condi1_o)
print("-------------------------------------------")
print("Se van a actualizar/crear los siguientes registros:")
print("Web de destino.: ",web_d)
print("Modelo migrado.: ",model_d)
print("Campo id anter.: ",idant_o)
print("===========================================")

# Busqueda en el odoo del origen los registros que cumplan con la condicion condi1_o todas las categorias en este caso []
# las buscamos en el destino, si existren le actualizamos los valores_update
# si no existen en el destino las creamos, con los valores_update despues del else.
registro_ids_o = sock_o.execute(dbname_o,uid_o,pwd_o,model_o,'search',condi1_o)
print ("Cantidad de", model_o," con la condicion: ", condi1_o, " leidos desde el origen:",len(registro_ids_o))

# Iniciar los contadores
x=0
j=0
ec=0
ea=0

for i in registro_ids_o:
    # Leemos la info de los registros en la base origen 
    print(" cada registro de origen lo llamamos i, contiene lo siguiente: ", i)
    print ("Verificando en el origen el modelo: ",model_o," el objeto con id: ", i)
    registro_data_o = sock_o.execute(dbname_o,uid_o,pwd_o,model_o,'read',i,campos)
    #obteniendo la ID original para buscar en el destino
    clave_o=registro_data_o['id']
    nombre_o=registro_data_o['name']
    symbol_o=registro_data_o['symbol']
    print ("Registro  Obtenido con clave: ", clave_o)
    print ("Registro  Obtenido con nombre_o: ", nombre_o)
    print ("Registro  Obtenido con symbol: ", symbol_o)

registro_ids_d = sock_d.execute(dbname_d,uid_d,pwd_d,model_d,'search',condi1_o)
print ("Cantidad de", model_d," con la condicion: ", condi1_o, " leidos desde el destino:",len(registro_ids_d))

for k in registro_ids_d:
    # Leemos la info de los registros en la base origen 
    print(" cada registro de origen lo llamamos k, contiene lo siguiente: ", k)
    print ("Verificando en el origen el modelo: ",model_o," el objeto con id: ", k)
    registro_data_d = sock_d.execute(dbname_d,uid_d,pwd_d,model_d,'read',k,campos)
    #obteniendo la ID original para buscar en el destino
    clave_d=registro_data_d['id']
    nombre_d=registro_data_d['name']
    symbol_d=registro_data_d['symbol']
    print ("Registro  Obtenido con clave: ", clave_d)
    print ("Registro  Obtenido con nombre_o: ", nombre_d)
    print ("Registro  Obtenido con symbol: ", symbol_d)
    print(registro_data_d)
