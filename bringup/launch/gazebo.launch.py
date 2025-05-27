from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, ExecuteProcess, RegisterEventHandler
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, Command,FindExecutable
from launch.event_handlers import OnProcessStart
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from ament_index_python.packages import get_package_share_directory
from launch_ros.parameter_descriptions import ParameterValue
from launch.conditions import IfCondition, UnlessCondition
import os


def generate_launch_description():
    
    declared_arguments = []
    declared_arguments.append(
        DeclareLaunchArgument(
            "gui",
            default_value="true",
            description="Start RViz2 automatically with this launch file.",
        )
    )

    gui = LaunchConfiguration("gui")

    pkg_path = get_package_share_directory('space_robot')
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [FindPackageShare("ros_gz_sim"), "/launch/gz_sim.launch.py"]),
        # launch_arguments={'gz_args': PathJoinSubstitution([
        #     pkg_path,
        #     'description',
        #     'worlds',
        #     'space_world.sdf'
        # ])}.items(),
        launch_arguments=[("gz_args", "-r -v 3 empty.sdf")],
        condition=IfCondition(gui)
    )
    gazebo_headless = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [FindPackageShare("rosz_gz_sim"), "/launch/gz_sim.launch.py"]
        ),
        launch_arguments=[("gz_args", "--headless-rendering -s -r -v 3 empty.sdf")],
        condition=UnlessCondition(gui)
    )

    spawn = Node(
        package='ros_gz_sim', 
        executable='create',
        arguments=[
            '-topic', '/robot_description',  # 必须的模型来源参数
            '-name', 'space_robot',
            '-allow_renaming', "true"
        ]
    )

    bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        parameters=[{
            'config_file': os.path.join(pkg_path, 'bringup', 'config', 'ros_gz_bridge.yaml'),
            'qos_overrides./tf_static.publisher.durability': 'transient_local',
        }],
    )

    # robot_description_content = Command([
    #     PathJoinSubstitution([FindExecutable(name='xacro')]),
    #     ' ',
    #     PathJoinSubstitution([pkg_path, 'description', 'urdf', 'space_robot.urdf.xacro']),
    #     " ",
    #     "use_gazebo:=true"
    # ])
    # robot_description = {'robot_description': robot_description_content}

    # robot_controllers = PathJoinSubstitution([
    #     FindPackageShare("space_robot"),
    #     "bringup",
    #     "config",
    #     "controllers.yaml",
    # ])

    # joint_state_broadcaster_spawner = Node(
    #     package="controller_manager",
    #     executable="spawner",
    #     arguments=["joint_state_broadcaster"],
    # )

    # robot_controller_spawner = Node(
    #     package="controller_manager",
    #     executable="spawner",
    #     arguments=["forward_position_controller", "--param-file", robot_controllers],
    # )

    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster", "--controller-manager", "/controller_manager"],
    )

    robot_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["forward_position_controller", "--controller-manager", "/controller_manager"],
    )

    # controller = Node(
    #     package='controller_manager',
    #     executable='ros2_control_node',
    #     parameters=[
    #         {"robot_description": robot_description}, 
    #         {"use_sim_time": True}  # 如果使用 Gazebo/Ignition 仿真，设为 True
    #     ],
    #     output="screen",
    # )

    # load_joint_state_controller = ExecuteProcess(
    #     cmd=['ros2', 'control', 'load_controller', '--set-state', 'active', 'joint_state_broadcaster'],
    #     output='screen'
    # )

    # load_joint_trajectory_controller = ExecuteProcess(
    #     cmd=['ros2', 'control', 'load_controller', '--set-state', 'active', 'velocity_controller'],
    #     output='screen'
    # )

    nodes = [
        gazebo,
        gazebo_headless,
        spawn,
        bridge,
        joint_state_broadcaster_spawner,
        robot_controller_spawner,
    ]
   
    return LaunchDescription(declared_arguments + nodes)