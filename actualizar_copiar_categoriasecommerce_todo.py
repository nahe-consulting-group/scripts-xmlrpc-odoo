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
campos = ['id', 'name', 'parent_id', 'sequence', 'display_name', 'child_id']

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
    print ("Registro  Obtenido: ", registro_data_o)
    #obteniendo la ID original para buscar en el destino
    clave=registro_data_o['id']
    nombre_o=registro_data_o['name']
    #busco la id del padre e hijas en el origen
    id_padre_o=registro_data_o['parent_id']
    id_hija_o=registro_data_o['child_id']
    #Busqueda por id_anterior en el destino para ver si existe y se actualiza o hay que crearlo.
    # si el ODOO DE DESTINO tiene mas campos requeridos puede fallar, pero se agregan en la variable campos. 
    # conviene importar antes de seguir instalando muchos modulos.
    # BUSCAMOS EN EL DESTINO SI EXISTE una categoria con el valor de idant_o (tiene que existir ente valor en el modelo) igual a clave
    registro_id_d = sock_d.execute(dbname_d,uid_d,pwd_d,model_d,'search',[(idant_o,'=',clave)])
    # si se econtro el registro_id_d se actualiza con nuevos valores
    if registro_id_d:
        #las categorias padre en el origen tienen patrent_id = False. por lo tanto si es false no hay que modificar ese valor. las hijas tienen una lista de id_padre_o. Si la categoria es padre no tocamos su parent id en destino.
        print (registro_data_o)
        # 'parent_id': nuevos_padres, las padres tienen por defecto False
        nuevos_padres=False
        # 'parent_id': nuevos_padres, las hijas tienen que encontrar a su padre en destino. por lo que es necesario migrar PRIMERO las padres y se usa condi1_o = [('parent_id','=', [0])]
        if (id_padre_o != False):
            id_padre_o_popeado=id_padre_o.pop(0)
            nuevos_padres=[]
            print(id_padre_o, " este es el valor de id_padre_o despues de popearlo")
            print(id_padre_o_popeado, "este es el valor de id_padre_o_popeado y lo vamos a usar para vuscar el nuevo id de su padre")
            condi_p=[(idant_o,'=',id_padre_o_popeado)]
            try:
                id_padre_d=sock_d.execute(dbname_d,uid_d,pwd_d,model_d,'search',condi_p)
                print("el valor de id_padre_d es: ", id_padre_d)
                id_padre_d_popeado=id_padre_d.pop(0)
                nuevos_padres=id_padre_d_popeado
                print ("el valor de nuevos_padres para este articulo es: ",nuevos_padres)
            except:
                print("no encontramos padre numero", id_padre_d_popeado)
            print('Nuevos padres',(nuevos_padres))
        else:
            print("la categoria es padre porque tiene id_padre_o = False ")
        print ("Actualizando registro: ",nombre_o)
        valores_update = {
            'name': registro_data_o['name'],
            'display_name': registro_data_o['display_name'],
            #'child_id': nuevos_hijos,
            'parent_id': nuevos_padres,
            #'sequence': registro_data_o['sequence'], ####ESTE O NO ANDA BIEN EN ODOO 11 O ALGO MAL HICE
            idant_o: registro_data_o['id']
            }
        #esta linea es la encargada de actualizar en el destino 
        try:
            return_id = sock_d.execute(dbname_d,uid_d,pwd_d,model_d,'write',registro_id_d,valores_update)
            print (return_id," exito al actualizar ",nombre_o)
        except:
            print("Error actualizando registro: ",nombre_o)
            ea+=1
        x+=1
    # si no se econtro el registro en el destino se crea
    else:
        print ("No se encontro en el destino: ", nombre_o," vamos a crearlo.")
        #las categorias no existen en el destino, por lo tanto primero las creamos y creamos las padres primero condi1_o = [('parent_id','=', [0])]
        nuevos_padres=False
        if (id_padre_o != False):
            id_padre_o_popeado=id_padre_o.pop(0)
            nuevos_padres=[]
            print(id_padre_o, " este es el valor de id_padre_o despues del pop")
            print(id_padre_o_popeado, "este es el valor de id_padre_o_popeado")
            condi_p=[(idant_o,'=',id_padre_o_popeado)]
            try:
                id_padre_d=sock_d.execute(dbname_d,uid_d,pwd_d,model_d,'search',condi_p)
                nuevos_padres=id_padre_d
                print ("el valor de nuevos_padres para este articulo es: ",nuevos_padres)
            except:
                print("no encontramos padre numero", id_padre_d)
            print('Nuevos padres',(nuevos_padres))
        nuevos_hijos=[]
        valores_update = {
        'name': registro_data_o['name'],
        'display_name': registro_data_o['display_name'],
        #'child_id': nuevos_hijos,
        #'parent_id': nuevos_padres,
        #'sequence': registro_data_o['sequence'],
        idant_o: registro_data_o['id']
        }
        #esta linea es la encargada de crear en el destino
        try:
            return_id = sock_d.execute(dbname_d,uid_d,pwd_d,model_d,'create',valores_update)
            print (return_id,"exito al crear ",nombre_o)
        except:
            print("Ha ocurrido un error al intentar crear el partner: ",nombre_o) 
            ec+=1
        j+=1
print("===========================================")
print ("Cantidad de registros actualizados: ",x)
print ("Cantidad de actualizados con error: ",ea)
print ("Cantidad de registros creados: ",j)
print (" Cantidad de errores al crear: ",ec)
print("===========================================")

print("ESTAS FUERON LAS CATEGORIAS con la condicion condi1_o = ", condi1_o)