from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, FindExecutable, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
from launch_ros.actions import Node


def generate_launch_description():
    package = "rrbot_controller_manager"
    model_package = "rrbot_description"

    # generate urdf from xacro
    robot_description = Command(
        [
            PathJoinSubstitution(FindExecutable(name="xacro")),
            " ",
            PathJoinSubstitution(
                [FindPackageShare(model_package), "urdf", "model.urdf.xacro"]
            ),
            " ",
            "use_gazebo:=true",
            " ",
            "controller_configs_for_gazebo:=",
            PathJoinSubstitution(
                [FindPackageShare(package), "config", "controller.yaml"]
            ),
        ]
    )

    # node to publish /robot_description and /tf (forward kinematics)
    # calculated from urdf and /joint_states
    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[{"robot_description": robot_description}],
    )

    # RViz2
    rviz2 = Node(
        package="rviz2",
        executable="rviz2",
        arguments=[
            "-d",
            PathJoinSubstitution(
                [FindPackageShare(model_package), "rviz", "view_robot.rviz"]
            ),
        ],
    )

    # Gazebo
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [FindPackageShare("gazebo_ros"), "/launch", "/gazebo.launch.py"]
        )
    )

    # spawn a rrbot model from /robot_description subscribe on Gazebo
    gazebo_spawner = Node(
        package="gazebo_ros",
        executable="spawn_entity.py",
        arguments=["-entity", "rrbot", "-topic", "robot_description"],
    )

    # node to publish /joint_states calculated from Gazebo
    joint_state_broadcaster = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "joint_state_broadcaster",
            "--controller-manager",
            "/controller_manager",
        ],
    )

    return LaunchDescription(
        [
            robot_state_publisher,
            rviz2,
            gazebo,
            gazebo_spawner,
            joint_state_broadcaster,
        ]
    )
