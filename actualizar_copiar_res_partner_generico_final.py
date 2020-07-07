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
condi1_o = [('active','=','true'),('id', '>', '10')] # ('id', '>', '10') las primeras 10 id son reservadas de cada instalacion ('is_company','=','true') para las compañias primero, luego para los individuos ('is_company','!=','true')
# campos que quiero migrar del odoo origen
campos = ['id', 'active', 'name', 'company_type', 'street', 'street2', 'city', 'state_id', 'responsability_id',
          'zip', 'country_id', 'image', 'website', 'function', 'phone', 'mobile', 'fax',
          'email', 'title', 'lang', 'comment', 'customer', 'supplier', 'notify_email', 'vat', 'document_type_id', 'document_number', 'property_product_pricelist']

# esto genera el contexto para que se conecte
gcontext = ssl._create_unverified_context()

# Get the uid origen de los datos. modificar weborigen por ip:puerto
sock_common_o = xmlrpc.client.ServerProxy ('http://www2.electronicajck.com/xmlrpc/common',context=gcontext)
uid_o = sock_common_o.login(dbname_o, user_o, pwd_o)

# Get the uid destino de los datos
sock_common_d = xmlrpc.client.ServerProxy ('http://127.0.0.1:8068/xmlrpc/common',context=gcontext)
uid_d = sock_common_d.login(dbname_d, user_d, pwd_d)

#reemplazar el valor de la ip o url del servidor de origen con su puerto
sock_o = xmlrpc.client.ServerProxy('http://www2.electronicajck.com/xmlrpc/object',context=gcontext)

#reemplazar el valor de la ip o url del servidor de destino con su puerto
sock_d = xmlrpc.client.ServerProxy('http://127.0.0.1:8068/xmlrpc/object',context=gcontext)

# Busqueda en el odoo del origen solo las companias primero y luego los individuos 
# Busqueda en el odoo del origen los registros que cumplan con la condicion condi1_o todas las en este caso []
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
    print ("Registro  Obtenido: ", registro_data_o['name'])
    #obteniendo la ID original para buscar en el destino
    clave=registro_data_o['id']
    nombre=registro_data_o['name']
    #aca nombramos variables para luego llamarlas dentro de valores_update, en especial las que devuelven un diccionario. registro_data_o[0]['document_type_id'] no me anda
    document_type_id_o=registro_data_o['document_type_id']
    if document_type_id_o:
    	document_type_id_o=registro_data_o['document_type_id']
    else:
    	document_type_id_o=[35]
    #las listas de precio hay que revisar los ID a mano para poder dejar andando el codigo. esta parte se deberia hacer mas generica pero no me salio 
    property_product_pricelist_o=registro_data_o['property_product_pricelist']
    if property_product_pricelist_o[0] == 3:# forzar precio gremio a 2 en la nueva
    	property_product_pricelist_o[0] = 2
    else:
    	property_product_pricelist_o=registro_data_o['property_product_pricelist']
    if property_product_pricelist_o[0] == 6:# forzar precio gremio a 2 en la nueva
    	property_product_pricelist_o[0] = 4
    else:
    	property_product_pricelist_o=registro_data_o['property_product_pricelist']
    responsability_id_o=registro_data_o['responsability_id']
    if responsability_id_o:
    	print("responsability_id_o es: ",responsability_id_o)
    else:
    	responsability_id_o= [6]
    country_id_o=registro_data_o['country_id']
    #argentina es el 10 en odoo 11 y el 11 en odoo 8
    if country_id_o:
    	if country_id_o[0] == 11:
    		country_id_o[0] = 10
    else:
    	country_id_o = [10]
    state_id_o=registro_data_o['state_id']
    if state_id_o:
    	if state_id_o[0] == 61: # 61 era buenos aires en odoo 8 sock_d.execute(dbname_d,uid_d,pwd_d,'res.country.state','search',[('name','=',property_product_pricelist_o[1])])
    		state_id_o[0] = 554 #554 es el caso de buenos aires en el odoo 11 que instale. 
    	else:
    		state_id_o = [554] # si no es de buenos aires lo dejo vacío para no cambiarle mal la provincia, mejor no tener el dato y preguntar en mi caso. 
    else:
    	state_id_o = [554] #si no tengo el dato fuerzo BS AS 
    #Busqueda por id_anterior en el destino para ver si existe y se actualiza o hay que crearlo.
    # si el ODOO DE DESTINO tiene mas campos requeridos puede fallar, pero se agregan en la variable campos. 
    # conviene importar antes de seguir instalando muchos modulos.
    # BUSCAMOS EN EL DESTINO SI EXISTE una categoria con el valor de idant_o (tiene que existir ente valor en el modelo) igual a clave
    registro_id_d = sock_d.execute(dbname_d,uid_d,pwd_d,model_d,'search',[(idant_o,'=',clave)])
    valores_update = {
        'active': registro_data_o['active'],
        'name': registro_data_o['name'],
        'property_product_pricelist': property_product_pricelist_o[0],
        'afip_responsability_type_id': responsability_id_o[0],
        'main_id_category_id': document_type_id_o[0],
        'main_id_number': registro_data_o['document_number'],
        'street': registro_data_o['street'],
        'street2': registro_data_o['street2'],
        'city': registro_data_o['city'],
        'country_id': country_id_o[0],
        'state_id': state_id_o[0],
        'zip': registro_data_o['zip'],
        #'image': registro_data_o['image'], #al pedo importar esto
        'website': registro_data_o['website'],
        'function': registro_data_o['function'],
        'phone': registro_data_o['phone'],
        'mobile': registro_data_o['mobile'],
        'fax': registro_data_o['fax'],
        'email': registro_data_o['email'],
        'title': registro_data_o['title'],
        'lang': registro_data_o['lang'],
        'comment': registro_data_o['comment'],
        'customer': registro_data_o['customer'],
        'supplier': registro_data_o['supplier'],
        'notify_email': registro_data_o['notify_email'],
        'vat': registro_data_o['vat']
        }

    # si se econtro el registro se actualiza
    if registro_id_d:
        print ("Actualizando registro: ",nombre)
        #esta linea es la encargada de actualizar en el destino 
        try:
            return_id = sock_d.execute(dbname_d,uid_d,pwd_d,'res.partner','write',registro_id_d,valores_update)
            print (return_id,"exito al actualizar ",nombre)
        except:
            print("Ha ocurrido un error al intentar actualizar el registro: ",nombre)
            ea+=1
        x+=1
    # si no se econtro el registro en el destino se crea
    else:
        print ("No se encontro en el destino: ",nombre," vamos a crearlo.")
        #esta linea es la encargada de crear en el destino
        try:
            return_id = sock_d.execute(dbname_d,uid_d,pwd_d,'res.partner','create',valores_update)
            print (return_id,"exito al crear ",nombre)
        except:
            print("Ha ocurrido un error al intentar crear el partner: ",nombre ) 
            ec+=1
        #print (registro_data_d)
        j+=1
print ("Cantidad de registros actualizados: ",x)
print ("Cantidad de actualizados con error: ",ea)
print ("Cantidad de registros creados: ",j)
print (" Cantidad de errores al crear: ",ec)