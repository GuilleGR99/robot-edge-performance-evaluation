#!/bin/bash

########################################
# Configuracion
########################################

WORKSPACE=~/catkin_ws
LOG_SIM="sim.log"

########################################
# Preparar entorno ROS
########################################

source /opt/ros/melodic/setup.bash
source $WORKSPACE/devel/setup.bash

export ROS_MASTER_URI=http://localhost:11311
export ROS_HOSTNAME=localhost

########################################
# Lanzar simulacion
########################################

echo "Lanzando simulacion..."

roslaunch summit_xl_gazebo summit_xl_sim_navigation.launch > $LOG_SIM 2>&1 &
LAUNCH_PID=$!

########################################
# Esperar a ROS master
########################################

echo "Esperando ROS master..."

until rostopic list >/dev/null 2>&1
do
  sleep 1
done

########################################
# Esperar a AMCL
########################################

echo "Esperando a AMCL..."

until rosnode list 2>/dev/null | grep -q "/robot/amcl"
do
  sleep 1
done

echo "AMCL listo"

########################################
# Relocalizacion global
########################################

echo "Llamando a global_localization..."

rosservice call /robot/global_localization
sleep 2

########################################
# Initial pose
########################################

echo "Publicando initial pose..."

rostopic pub -1 /robot/initialpose geometry_msgs/PoseWithCovarianceStamped "
header:
  frame_id: 'robot_map'
pose:
  pose:
    position: {x: 0.0, y: 0.0, z: 0.0}
    orientation: {x: 0.0, y: 0.0, z: -0.0109889745103, w: 0.999939619397}
  covariance: [0.2333590096797593, 0.004243860337707517, 0.0, 0.0, 0.0, 0.0,
               0.004243860337708405, 0.25837236350461, 0.0, 0.0, 0.0, 0.0,
               0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
               0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
               0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
               0.0, 0.0, 0.0, 0.0, 0.0, 0.06524389960887333]
" > /dev/null 2>&1

sleep 3

########################################
# Movimiento para convergencia AMCL
########################################

echo "Moviendo robot para convergencia..."

rostopic pub -r 10 /robot/cmd_vel geometry_msgs/Twist "
linear:
  x: 0.1
angular:
  z: 0.5
" > /dev/null 2>&1 &

MOVE_PID=$!

sleep 6
kill $MOVE_PID

echo "Esperando estabilizacion..."
sleep 5

########################################
# Funcion esperar goal
########################################

wait_for_goal () {

    echo "Esperando llegada al objetivo..."

    while true
    do
        STATUS=$(timeout 2 rostopic echo -n1 /robot/move_base/status 2>/dev/null \
                 | grep "status:" \
                 | tail -1 \
                 | awk '{print $2}')

        if [ "$STATUS" = "3" ]; then
            echo "Objetivo alcanzado"
            break
        fi

        sleep 1
    done
}

########################################
# Funcion enviar goal (con orientacion)
########################################

send_goal () {

  X=$1
  Y=$2
  YAW=$3

  echo "Enviando goal -> x:$X y:$Y yaw:$YAW"

  # Conversion yaw -> cuaternion
  Z=$(python3 - <<EOF
import math
print(math.sin($YAW/2))
EOF
)

  W=$(python3 - <<EOF
import math
print(math.cos($YAW/2))
EOF
)

  rostopic pub -1 /robot/move_base_simple/goal geometry_msgs/PoseStamped "
header:
  frame_id: 'robot_map'
pose:
  position: {x: $X, y: $Y, z: 0}
  orientation: {x: 0, y: 0, z: $Z, w: $W}
" > /dev/null 2>&1

  sleep 2
  wait_for_goal
}

########################################
# Trayectoria
########################################

for i in {1..5}
do

echo "-----------------------------"
echo "Inicio de vuelta $i"
echo "-----------------------------"

echo "Destino $i A"
send_goal 2.5 0.75 0

echo "Destino $i B"
send_goal 4.5 4.5 3.14

echo "Destino $i C"
send_goal 0 4.5 3.14

echo "Destino $i D"
send_goal -4.5 4.5 4.71

echo "Destino $i E"
send_goal -4.5 0 4.71

echo "Destino $i F"
send_goal -4.5 -4.5 0

echo "Destino $i G"
send_goal 0 -4.5 0

echo "Destino $i H"
send_goal 4.5 -4.5 1.57

echo "Destino $i I"
send_goal 2.5 -0.75 3.14

echo "Destino $i origen"
send_goal 0 0 0

echo "Vuelta $i completada"

done

########################################
# Finalizacion
########################################

sleep 5
kill $LAUNCH_PID

echo "Simulacion finalizada"
