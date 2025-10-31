
flujo de funciones de la pi getway


1 manejo de formulario de ingreso de datos del proeycto 
        inputs
    - titulo del proyecto 
    - description del proyecto (si se peude en formato karkdown)
    - cargue de archivos relacionados (pdf, md, txt)

2 creacion del proeytco y centralizacion del contesto
    teniendo los inputs del formulario realizamos 2 pasos

    2.1 creamos el hilo de ejecucion

    2.2 cargamos los documentos relacionados al proyetco en elservici de objetos (minio) usamos el id del hilo como refernecia para los documentos en su nombre, de aca recibiriamos las url de acceso a los documentos 

    2.3 ejecutamos el hilo y pasmaos los imputs correspondientes 
        - titulo del proyetco 
        - descripcion 
        - lista de enlaces de axcceso a los documentos relacionados 
    


3 ingesta de informacion en el estado y manejo de contexto del profyetco 
    
    ---en paralelo 
    |----------3.1 ingreso de los inputs al estado 
    |----------3.2 a partir de los documentos relevantes los vectorizamos 

4 seguimos con el flujo del agente norma 
    NOTA aplicra las siguientes funciones depues  
    -  agregar la funcion correspondinte al guardafdo de los reportes generales y especificos en el servicio de objetos 
    - realizar el vectorizado de los reportes generados (general y especifico)
    - implementar sistema de rag en el nodo dechat 


docker-compose exec api_gateway python manage.py migrate