#!/bin/bash

########################################
# Configuracion
########################################

WORKSPACE=~/catkin_ws
LOG_SIM="sim.log"
LOG_ADAPTER1="twist_to_stamped.log"
LOG_ADAPTER2="stamped_to_twist.log"

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

roslaunch summit_xl_gazebo summit_xl_sim_navigation.launch gazebo_gui:=false launch_rviz:=false > $LOG_SIM 2>&1 &
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
# Lanzar adaptadores
########################################

echo "Lanzando adaptadores..."

rosrun latency_tools twist_to_stamped.py > $LOG_ADAPTER1 2>&1 &
ADAPTER1_PID=$!

rosrun latency_tools stamped_to_twist.py > $LOG_ADAPTER2 2>&1 &
ADAPTER2_PID=$!

########################################
# Esperar a adaptadores
########################################

echo "Esperando cmd_vel..."

until rostopic list 2>/dev/null | grep -q "/robot/move_base/cmd_vel"
do
  sleep 1
done

echo "cmd_vel disponible"

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
# Funcion enviar goal
########################################

send_goal () {

  X=$1
  Y=$2
  YAW=$3

  echo "Enviando goal -> x:$X y:$Y yaw:$YAW"

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

  rostopic pub -1 /robot/move_base_simple/goal_stamped geometry_msgs/PoseStamped "
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

send_goal 2.5 0.75 0
send_goal 4.5 4.5 3.14
send_goal 0 4.5 3.14
send_goal -4.5 4.5 4.71
send_goal -4.5 0 4.71
send_goal -4.5 -4.5 0
send_goal 0 -4.5 0
send_goal 4.5 -4.5 1.57
send_goal 2.5 -0.75 3.14
send_goal 0 0 0

echo "Vuelta $i completada"

done

########################################
# Finalizacion
########################################

sleep 5

kill $ADAPTER1_PID
kill $ADAPTER2_PID
kill $LAUNCH_PID

echo "Simulacion finalizada"