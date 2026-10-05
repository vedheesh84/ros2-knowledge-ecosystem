from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'learning_lifecycle'

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
    description='ROS2 Learning: Lifecycle nodes for deterministic robots',
    license='MIT',
    entry_points={
        'console_scripts': [
            'lifecycle_sensor_node = learning_lifecycle.lifecycle_sensor_node:main',
            'lifecycle_controller_node = learning_lifecycle.lifecycle_controller_node:main',
        ],
    },
)
