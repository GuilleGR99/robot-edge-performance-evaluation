# Información general
## Tools
- ROS 1
- ROS nodes -> move_base
- Gazebo
- RViz -> 2D Nav Goal
- Summit XL robot
## Questions
- Cual es la diferencias entre el planificador locar y global
- Que sensores tiene y que datos recoge cada uno. Como se integra cada uno de estos datos
- Como interactura TF Tree en todo el sistema
- Que ocurre dentro de move_base
- Que es ROS. Caracteristicas principales. Integración. Comunicación. Nodos de la comunidad. Lenguajes.
- ROS 1 vs ROS 2 diferencias estructurales (en profundidad que implica este cambio)
- Estructura de carpetas ROS
- Como se integran nuevos nodos ROS en el sistema
- Que valores QoS pueden generarse en la simulación
- como funciona el modelo topic - suscriber

## Comandos
```bash
#añade los paquetes del workspace al entorno de ROS
source ~/catkin_ws/devel/setup.bash
#lanzamiento simulacion
roslaunch summit_xl_gazebo summit_xl_sim_navigation.launch
#verifica que los nodos estan activos
rosnode list
#verifica los topics existentes
rostopic list
/home/summitxlq/catkin_ws/src/summit_xl_common/summit_xl_localization/maps/turtlebot3/qworld.yaml
/home/summitxlq/catkin_ws/src/summit_xl_sim/summit_xl_gazebo/worlds/qlearning.world
/home/summitxlq/catkin_ws/src/summit_xl_sim/summit_xl_gazebo/launch/summit_xl_sim_navigation.launch
```


## Arquitectura ROS 1 Summit XL
Arquitectura en capas en la que cada una de ellas esta conformada por nodos especializados en una tarea. Tanto los nodos de una capa como las capas se interconectan por topics.
SIMULATION
   │
   ▼
ROBOT MODEL
   │
   ▼
LOCALIZATION
   │
   ▼
NAVIGATION
   │
   ▼
CONTROL

## Consideraciones
- La versión de ROS 1 es melodic
- Una de las limitaciones de ROS 1 es que concibe cada nodo como un proceso completo impidiendo que se desglose en procesos mas pequeños.

# Reuniones
## 19/02/24

### To do
- ROS1 buscar un modulo para el calculo de latencias en robot, cloud, edge. 
- La migración de ROS1 a ROS2 es probable que ocurra en marzo/abril pero no es seguro.
- Debo centrarme en la parte teorica. Diferencias entre ROS1 y ROS2. Como hacen lo optimización de funciones.
- Funciones ya existentes para no hacerlo yo sino simplemente integrar lo ya existente.
- Githubs con codigos sobre la medición de latencias. Herramientas existentes y posibles desarrollos.
- **proxima reunion**: El estado del arte: ROS1 y ROS2, las funciones existente.
- Eliminar referencias a ros2 del titulo y emulado. ros 1/2. rendimiento de aplicaciones. Red real y ros 1
- diseños de simulación robot-edge ros 1
- mirar fechas para registrar el trabajo
- isntalaciĺon de ros1 jay
- Mirar que equipamiento tiene el summit-xl empleado y cambiar esto en la sección 3.2

## 05/03/26
### ¿Que he hecho esta semana?
- He terminado de leer gran parte de la literatur. (los documentos que el iTEAM compartio conmigo, menos los relacionados explicitamente con ROS 2)
- He leido la documentación de ROS
- La sección 2. Estado Del Arte esta en estado de revisión
- En cuanto a la sección 3. Arquitectura del sistema propuesto. La subsecciónes relacionadas con Plataforma Hardware Summit XL y Capa de red 5G privada estan en estado de revisión

### ¿Que voy a hacer la siguiente?
- Completar la sección 1. introducción
- Entender la relación entre los nodos del sistema del robot Summit XL e identificar de forma cuantitativa los procesos que requieren mayor carga computacional. A partir de este análisis se seleccionarán los nodos candidatos a ser desplazados al edge mediante una distribución estática.

### Dudas
¿Dónde debe ubicarse el nodo de edge computing dentro de la arquitectura del sistema?
¿Qué criterios deben utilizarse para decidir el offloading de tareas desde el robot hacia el edge?  
¿La distribución de tareas entre robot y edge debe ser estática o dinámica?

### Comentarios sobre la reunión
- Los criterios a emplear para decidir el offloading de procesos son la carga del procesador y la frecuencia.
- La distribución de tareas sera estatica.
- Utilizar ns3 y iperf para la simulación de la red 5G

## 12/03/26
### ¿Que he hecho esta semana?
- Familiarizarme con la implementación de ROS en el summit 
- Hacer el setup experimental

### ¿Que voy a hacer la siguiente?
- Una vez validado setup tomar medidas, limpiar datos y hacer graficas
- En base a ello se decide el offloading.

### Dudas
- ¿Como se conecta el summit xl a la red 5GSA? Debe debe de tener alguna interfaz para ello. (Esta información debe actulizarse en la sección 3.2.1) modem 5g ehtehrnet
- En la simulación existen varios mapas. Debería de considerar alguno de ellos sobre el resto?
- Que algoritmos para el local planner debo usar? TEB o QLearning?
- Tiene sentido el setup experimental? Las herramientas que empleo para medir los procesos son apropiadas? 

mirar herramienta latencias
teltonika rutx50
TEB vs qlearning
turtble3 sino diferencias teb y wlearing.
