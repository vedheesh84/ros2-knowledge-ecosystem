from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'learning_integration'

setup(
    name=package_name,
    version='1.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob(os.path.join('launch', '*.launch.py'))),
        (os.path.join('share', package_name, 'config'), glob(os.path.join('config', '*.yaml'))),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='ROS2 Learner',
    maintainer_email='learner@ros2.org',
    description='ROS2 Learning: Complete integration capstone',
    license='MIT',
    entry_points={
        'console_scripts': [
            'robot_brain_node = learning_integration.robot_brain_node:main',
            'sensor_fusion_node = learning_integration.sensor_fusion_node:main',
            'command_executor_node = learning_integration.command_executor_node:main',
        ],
    },
)
