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
model_o = 'stock.quant' # nombre del modelo de origen
model_d = 'stock.quant' #nombre del modelo del destino
idant_o = 'x_id_anterior' # nombre del campo donde se almacena el id del anterior, se debe crear en el modelo del destino
# select product_id, qty, location_id from stock_quant where location_id in (15,22,28,36)
condi_o = [('location_id','=',12)] # condicion de los registros a migrar

# campos a tener en cuenta

campos = ['product_id', 'qty', 'location_id', 'in_date']

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
print("Campo id anter.: ",idant_o)
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
    print ("Verificando",model_o,"id:", i)
    registro_data_o = sock_o.execute(dbname_o,uid_o,pwd_o,model_o,'read',i,campos)
    print('Registro leido:',registro_data_o['product_id'],'|',registro_data_o['qty'],'|',registro_data_o['location_id'])
    
    #obteniendo el nuevo id del producto.template migrado
    condi_pro = [('x_id_anterior','=',registro_data_o['product_id'][0])]
    product_id = sock_d.execute(dbname_d,uid_d,pwd_d,'product.template','search',condi_pro)
    
    # si se econtro el producto hace el resto de las tareas
    if product_id:
        # obteniendo el id del producto.producto en el destino
        condi_pro_p = [('product_tmpl_id','=',product_id[0])]
        product_id_p = sock_d.execute(dbname_d,uid_d,pwd_d,'product.product','search',condi_pro_p)
        
        #obteniendo el nuevo id la ubicacion migrado
        #condi_loc = [('x_id_anterior','=',registro_data_o['location_id'])]
        #location_id = sock_d.execute(dbname_d,uid_d,pwd_d,'stock.location','search',condi_loc)
        #en mi caso location_id nuevo es 1 un solo inventario por eso dejo comentado lo anterio
        location_id = [14]
        print("El valor de product_id_p[0] es: ",product_id_p[0])
        print("El valor de registro_data_o['qty'] es: ",registro_data_o['qty'])
        print("El valor de location_id es: ",location_id)
        #estos valores_update son todos los que se van actualizar/crear para los registros
    
        valores_update = {
            'product_id': product_id_p[0],
            'quantity': registro_data_o['qty'],
            'in_date': registro_data_o['in_date'],
            'location_id': location_id[0]
            }
        print(valores_update)
        print ("Creando registro para producto: ",product_id_p)
        #esta linea es la encargada de crear en el destino
        try:
            return_id = sock_d.execute(dbname_d,uid_d,pwd_d,model_d,'create',valores_update)
            print (return_id)
        except:
            print("Error creando registro: ",product_id) 
            ec+=1
        j+=1
print ("=======================================")
print ("Cantidad registros actualizados: ",x)
print ("Cantidad s/actualizar con error: ",ea)
print ("Cantidad de registros creados..: ",j)
print ("Cantidad no creados con error..: ",ec)
print ("=======================================")