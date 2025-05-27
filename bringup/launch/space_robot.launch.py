from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution, LaunchConfiguration, Command, FindExecutable
from launch.conditions import IfCondition
from ament_index_python.packages import get_package_share_directory
from launch_ros.substitutions import FindPackageShare
from launch_ros.parameter_descriptions import ParameterValue

import os


def generate_launch_description():
    # Declare arguments
    declared_arguments = []
    declared_arguments.append(
        DeclareLaunchArgument(
            "gui",
            default_value="true",
            description="Start RViz2 automatically with this launch file.",
        )
    )

    # Initialize Arguments
    gui = LaunchConfiguration("gui")

    pkg_path = get_package_share_directory('space_robot')
    
    joint_state_publisher = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        parameters=[{'use_sim_time': False}],
        # 当其他节点提供 joint_states 时，添加以下行：
        # remappings=[('/joint_states', '/dummy_joint_states')]  # 重映射以避免冲突
    )

    # Get URDF via xacro
    robot_description_content = Command(
        [
            PathJoinSubstitution([FindExecutable(name="xacro")]),
            " ",
            PathJoinSubstitution(
                [FindPackageShare("space_robot"), "description", "urdf", "space_robot.urdf.xacro"]
            ),
            " ",
            "use_gazebo:=true",
        ]
    )
    robot_description = {"robot_description": robot_description_content}

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output="screen",
        parameters=[robot_description]
    )

    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_path, 'bringup', 'launch', 'gazebo.launch.py')),
            # launch_arguments={'gz_args': PathJoinSubstitution([
            #     pkg_path,
            #     'models',
            #     'worlds',
            #     'space_world.sdf'
            # ])}.items(),
            launch_arguments={'gui': gui}.items(),
    )

    rviz_config_file = PathJoinSubstitution(
        [FindPackageShare("space_robot"), 'bringup', 'config', 'space_robot.rviz']
    )

    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config_file],
        condition=IfCondition(gui)
    )

    nodes = [
        joint_state_publisher,
        robot_state_publisher,
        gz_sim,
        rviz,
    ]
    
    return LaunchDescription(declared_arguments + nodes)