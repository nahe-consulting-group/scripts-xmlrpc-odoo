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
model_o = 'product.template' # nombre del modelo de origen
model_d = 'product.template' #nombre del modelo del destino
idant_o = 'x_id_anterior' # nombre del campo a usar en el destino para almacenar id anterior, dejar vacio si no se usa. (tiene que ser un campo existente en el modelo model_d)
#este campo hay que crearlo en el modelo 
#categ_id_o = 'x_child_id_anterior'
# Es necesario crear el campo x_id_anterior en el model_d para usarlo en la variable idant_o
condi1_o = [('website_published', '!=', False)] # se labura con los padres  parent_id = False
# campos que quiero migrar del odoo origen
# campos a tener en cuenta casos especiales.
# company_type: puede tener dos valores [person,company] es importante usar para ('id', '>', '10')
#               primero se deben migrar todas las empresas is_company = true
#               segundo se deben migrar todas las personas is_company != true  (no se pone false)
# estos campos son para res.partner  hay que modificarlos para otos modelos o casos de uso. 
campos = ['id', 'name', 'qty_available', 'x_id_anterior']

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

for i in registro_ids_o:
    # Leemos la info de los registros en la base origen 
    print(" cada registro de origen lo llamamos i, contiene lo siguiente: ", i)
    print ("Verificando en el origen el modelo: ",model_o," el objeto con id: ", i)
    registro_data_o = sock_o.execute(dbname_o,uid_o,pwd_o,model_o,'read',i,campos)
    print("este es el registro_data_o: ",registro_data_o)
    cantidad_actual_origen = registro_data_o['qty_available']
    print("la cantidad_actual es: ",cantidad_actual_origen)
    clave=registro_data_o['id']
    print("el id en origen es: ",clave)
    registro_id_d = sock_d.execute(dbname_d,uid_d,pwd_d,model_d,'search',[(idant_o, '=', clave)])
    print("este es el registro_id_d: ",registro_id_d, "del producto con id en el origen: ",clave,"su cantidad_actual_origen es: ",cantidad_actual_origen)
    condi_prod_prod = [('product_tmpl_id','=',registro_id_d[0])]
    product_prod_id_d = sock_d.execute(dbname_d,uid_d,pwd_d,'product.product','search',condi_prod_prod)
    print("product_prod_id_d es: ",product_prod_id_d)
    if cantidad_actual_origen > 0:

        location_id = [14]
   
        valores_update = {
            'product_id': product_prod_id_d[0],
            'quantity': cantidad_actual_origen,
          #  'in_date': registro_data_o['in_date'],
            'location_id': location_id[0]
            }
        print(valores_update)
        print ("Creando registro para producto: ",product_prod_id_d)
        #esta linea es la encargada de crear en el destino
        try:
            return_id = sock_d.execute(dbname_d,uid_d,pwd_d,'stock.quant','create',valores_update)
            print (return_id)
        except:
            print("Error creando registro: ",product_prod_id_d) 