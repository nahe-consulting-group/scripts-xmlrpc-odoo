#!/opt/odoo/odoo11-venv/bin/python
# CUIDADO elegir bin del python correcto
# modificar la primer linea con which python.
# si está en un enviroment de pyhton usar la primer linea 
# Este script se testeo del 9 al 11 y anduvo. Tambien del 10 al 11 anduvo. Tengo que probar en odoo 8 a 11
import sys
import xmlrpc.client
import ssl

#user_o = 'completar' #el usuario de odoo origen
#user_d = 'completar' #el usuario de odoo destino
#pwd_o = 'completar' # contrasenia de usuario odoo origen
#pwd_d = 'completar' # contrasenia de usuario destino
#dbname_o = 'completar'  # nombre de base de datos origen
#dbname_d = 'completar' # nombre de base de datos destino
#web_o = 'completar' # ip o dir web del origen
#web_d = 'completar' # ip o dir web del destino
# datos de los modelos y campos
#model_o = 'completar' # nombre del modelo de origen
#model_d = 'completar' #nombre del modelo del destino
#idant_d = 'completar' # nombre del campo donde se almacena id anterior , se debe crear en el modelo destino
#condi_o = [('active','=','true'),('is_company','=','true')] # condicion de los registros a migrar
# variable para controlar si solo mostrar o mostrar y actualizar en el destino
#modo = 9 # 0:solo mostrar datos del origen, 1: mostrar y actualizar en el destino

# campos que quiero migrar del odoo origen

# variable para controlar si solo mostrar o mostrar y actualizar en el destino
modo = 0 # 0:solo mostrar datos del origen, 1: mostrar y actualizar en el destino

# campos a tener en cuenta

campos = ['id', 'name','child_id', 'parent_id', 'parent_left', 'parent_right', 'type']

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
print("Condicion regis: ",condi_o)
print("-------------------------------------------")
print("Se van a actualizar/crear los siguientes registros:")
print("Web de destino.: ",web_d)
print("Modelo migrado.: ",model_d)
print("Campo id anter.: ",idant_d)
print("===========================================")

# Busqueda en el odoo del origen los registros que cumplan con la condicion
registro_ids_o = sock_o.execute(dbname_o,uid_o,pwd_o,model_o,'search',condi_o)
print ("Cantidad de", model_o,"leidos desde el origen:",len(registro_ids_o))

# Iniciar los contadores
x=0
j=0
ec=0
ea=0

for i in registro_ids_o:
    # Leemos la info de los registros en la base origen
    registro_data_o = sock_o.execute(dbname_o,uid_o,pwd_o,model_o,'read',i,campos)
    print('=================================')
    print ('Registro leido del origen:',registro_data_o[0])
    
    #obteniendo el nuevo id del modelo destino
    condi_des = [(idant_d,'=',i)]
    registro_id_d = sock_d.execute(dbname_d,uid_d,pwd_d,model_d,'search',condi_des)
    print ('Id registro leido en destino:',registro_id_d)
    
    # si encuentra el ID en el destino lo actualiza solo el parent_id
    if registro_id_d:
        # obteniendo el registro en del destino
        registro_data_d = sock_d.execute(dbname_d,uid_d,pwd_d,model_d,'read',registro_id_d,campos)
        print ('Registro existe en el destino:',registro_data_d)
        if registro_data_o[0]['parent_id']:
            print ('Valor parent_id del origen:',registro_data_o[0]['parent_id'])
            condi_pad = [(idant_d,'=',registro_data_o[0]['parent_id'][0])]
            print ('Valor parent_id el destino:', condi_pad)
            regis_pad = sock_d.execute(dbname_d,uid_d,pwd_d,model_d,'search',condi_pad)
            if regis_pad:
                print ('Registro padre encontrado en el destino:',regis_pad[0])
                valores_update = {'parent_id': regis_pad[0]}
                return_id = sock_d.execute(dbname_d,uid_d,pwd_d,model_d,'write',registro_id_d,valores_update)
                print (return_id)
        x+=1
    else:     # si no lo encontró debo crearlo en el destino
        #estos valores_update son todos los que se van crear para los registros
        valores_update = {
            'name': registro_data_o[0]['name'],
            'type': registro_data_o[0]['type'],
            'x_id_ant': i
        }
        regis_des = sock_d.execute(dbname_d,uid_d,pwd_d,model_d,'create',valores_update)
        print ('nuevo registro creado:',regis_des)
        j+=1

print ("=======================================")
print ("Cantidad registros actualizados: ",x)
print ("Cantidad s/actualizar con error: ",ea)
print ("Cantidad de registros creados..: ",j)
print ("Cantidad no creados con error..: ",ec)
print ("=======================================")