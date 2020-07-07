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
condi1_o = [('website_published', '!=', False)] # se labura con los padres  parent_id = False
# campos que quiero migrar del odoo origen
# campos a tener en cuenta casos especiales.
# company_type: puede tener dos valores [person,company] es importante usar para ('id', '>', '10')
#               primero se deben migrar todas las empresas is_company = true
#               segundo se deben migrar todas las personas is_company != true  (no se pone false)
# estos campos son para res.partner  hay que modificarlos para otos modelos o casos de uso. 
campos = ['id', 'name','sale_ok', 'purchase_ok', 'type', 'default_code', 'description', 'sale_price_currency_id', 'list_price_type_currency_id', 'website_published',
          'standard_price', 'list_price', 'image_medium', 'image', 'barcode', 'taxes_id', 'supplier_taxes_id', 'seller_ids', 'categ_id', 'uom_id', 'uom_po_id',
          'sale_line_warn', 'product_variant_ids', 'purchase_line_warn', 'responsible_id', 'type', 'public_categ_ids', 'display_name', 'tracking', 'replenishment_cost_type']

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
    print ("Registro  Obtenido: ", registro_data_o['name'])
    #obteniendo la ID original para buscar en el destino
    clave=registro_data_o['id']
    nombre_o=registro_data_o['name']
    sale_price_currency_id_o=registro_data_o['sale_price_currency_id']
    if sale_price_currency_id_o[0] == 55:
        sale_price_currency_id_o[0] = 173 #173 es el id de la moneda creada en el destino
        print("cambiamos el valor de moneda que era 55 a 173 para BLU")
    else:
        print("no se ejecuto el if para BLU")
    uom_id_o=registro_data_o['uom_id']
    uom_po_id_o=registro_data_o['uom_po_id']
    #Busqueda por id_anterior en el destino para ver si existe y se actualiza o hay que crearlo.
    # si el ODOO DE DESTINO tiene mas campos requeridos puede fallar, pero se agregan en la variable campos. 
    # conviene importar antes de seguir instalando muchos modulos.
    # BUSCAMOS EN EL DESTINO SI EXISTE una categoria con el valor de idant_o (tiene que existir ente valor en el modelo) igual a clave
    registro_id_d = sock_d.execute(dbname_d,uid_d,pwd_d,model_d,'search',[(idant_o,'=',clave)])
    # si se econtro el registro_id_d se actualiza con nuevos valores
    if registro_id_d:
        print ("Encontrado en el nuevo servidor", clave, "con nombre", nombre_o,"lo vamos a actualizar")
        #busca el nuevo id de public_categ_ids en el destino
        regis_cat = False
        if registro_data_o['public_categ_ids']:
            print ('Valor public_categ_ids del origen:',registro_data_o['public_categ_ids'][0])
            condi_cat = [(idant_o,'=',registro_data_o['public_categ_ids'][0])]
            print ('Busqueda de public_categ_ids el destino:', condi_cat)
            regis_cat = sock_d.execute(dbname_d,uid_d,pwd_d,'product.public.category','search',condi_cat)
            print("el valor id de product.public.category NUEVO es: ",regis_cat)
            #regis_cat_pop = regis_cat.pop(0)
        # si encontro el nuevo id de categoria en el destino
        valores_update = {
            'name': registro_data_o['name'],
            #'categ_id': registro_data_o['categ_id'], #revisar en 8 y 11 como se llama y cuales son  
            'sale_ok': registro_data_o['sale_ok'],
            'description': registro_data_o['description'],
            'image_medium': registro_data_o['image_medium'],
            'list_price': registro_data_o['list_price'], #este es el precio que mi cliente tiene como precio publico en su odoo 8 de el se calculan los demas. 
            #'standard_price': registro_data_o['standard_price'], #creo que no es util en odoo 11 o es relacionado con otro
            'type': registro_data_o['type'],
            'website_published': registro_data_o['website_published'],
            'taxes_id': registro_data_o['taxes_id'],#este es iva ventas pero los ID pueden cambiar revisar esto  account.tax revisar ID origen y destino 
            'supplier_taxes_id': registro_data_o['supplier_taxes_id'],# este es iva comrpas pero los ID pueden cambiar revisar esto  account.tax revisar ID origen y destino 
            'public_categ_ids': [(6, 0, regis_cat)], #ESTAS SON LAS CATEGORIAS DE ECOMMERCE O CATEGORIAS PUBLICAS DE LA VERSION 9. actualizar_copiar_caregoriasecommerce.py 
            'purchase_ok': registro_data_o['purchase_ok'],
            'display_name': registro_data_o['display_name'],
            'list_price_type_currency_id': registro_data_o['list_price_type_currency_id'], #buscarlo en odoo 11 list_price_type_currency_id
            'force_currency_id': sale_price_currency_id_o[0], #sale_price_currency_id_o:  [55, 'BLU'] con foce_currency_id es [173, 'BLU'] en el 11
            'uom_id': uom_id_o[0],
            'uom_po_id': uom_po_id_o[0],
            #'tracking': registro_data_o['tracking'],
            #'sale_line_warn': registro_data_o['sale_line_warn'],
            #'responsible_id': registro_data_o['responsible_id'],
            #'replenishment_cost_type': registro_data_o['replenishment_cost_type'],
            #'product_variant_ids': registro_data_o['product_variant_ids'],
            #'purchase_line_warn': registro_data_o['purchase_line_warn'],
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
        #busca el nuevo id de public_categ_ids en el destino
        regis_cat = False
        if registro_data_o['public_categ_ids']:
            print ('Valor public_categ_ids del origen:',registro_data_o['public_categ_ids'][0])
            condi_cat = [(idant_o,'=',registro_data_o['public_categ_ids'][0])]
            print ('Busqueda de public_categ_ids el destino:', condi_cat)
            regis_cat = sock_d.execute(dbname_d,uid_d,pwd_d,'product.public.category','search',condi_cat)
            print("el valor id de product.public.category NUEVO es: ",regis_cat)
        valores_update = {
        'name': registro_data_o['name'],
        'display_name': registro_data_o['display_name'],
        #'categ_id': registro_data_o['categ_id'],
        #'uom_id': registro_data_o['uom_id'],
        #'uom_po_id': registro_data_o['uom_po_id'],
        'type': registro_data_o['type'],
        #'tracking': registro_data_o['tracking'],
        #'sale_line_warn': registro_data_o['sale_line_warn'],
        #'responsible_id': registro_data_o['responsible_id'],
        #'replenishment_cost_type': registro_data_o['replenishment_cost_type'],
        #'product_variant_ids': registro_data_o['product_variant_ids'],
        #'purchase_line_warn': registro_data_o['purchase_line_warn'],
        #'product_public_category': regis_cat,
        idant_o: registro_data_o['id']
        }
        #esta linea es la encargada de crear en el destino
        try:
            return_id = sock_d.execute(dbname_d,uid_d,pwd_d,model_d,'create',valores_update)
            print (return_id,"exito al crear ",nombre_o)
        except:
            print("Ha ocurrido un error al intentar crear el producto: ",nombre_o) 
            ec+=1
        j+=1
print("===========================================")
print ("Cantidad de registros actualizados: ",x)
print ("Cantidad de actualizados con error: ",ea)
print ("Cantidad de registros creados: ",j)
print (" Cantidad de errores al crear: ",ec)
print("===========================================")

print("ESTAS FUERON LAS CATEGORIAS con la condicion condi1_o = ", condi1_o)