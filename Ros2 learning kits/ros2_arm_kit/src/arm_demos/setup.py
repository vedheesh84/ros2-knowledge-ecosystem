from setuptools import setup

package_name = 'arm_demos'

setup(
    name=package_name,
    version='1.0.0',
    packages=[package_name, package_name + '.breakers'],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Vedheesh B',
    maintainer_email='vedheesh@intelligentsystems.io',
    description='Progressive educational manipulation demos and failure breakers for the robotic arm kit.',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'demo_01_joint_control = arm_demos.demo_01_joint_control:main',
            'demo_02_forward_kinematics = arm_demos.demo_02_forward_kinematics:main',
            'demo_03_inverse_kinematics = arm_demos.demo_03_inverse_kinematics:main',
            'demo_04_gripper_action = arm_demos.demo_04_gripper_action:main',
            'demo_05_moveit_planning = arm_demos.demo_05_moveit_planning:main',
            'demo_06_pick_place = arm_demos.demo_06_pick_place:main',
            'demo_07_teleoperation_mirroring = arm_demos.demo_07_teleoperation_mirroring:main',
            'demo_08_imitation_learning_recorder = arm_demos.demo_08_imitation_learning_recorder:main',
            'demo_09_trajectory_playback_policy = arm_demos.demo_09_trajectory_playback_policy:main',
            'break_joint_limits = arm_demos.breakers.break_joint_limits:main',
            'break_ik_singularity = arm_demos.breakers.break_ik_singularity:main',
            'break_gripper_stall = arm_demos.breakers.break_gripper_stall:main',
            'break_trajectory_timing = arm_demos.breakers.break_trajectory_timing:main',
        ],
    },
)
