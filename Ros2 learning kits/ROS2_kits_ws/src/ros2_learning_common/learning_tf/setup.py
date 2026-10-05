from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'learning_tf'

setup(
    name=package_name,
    version='1.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob(os.path.join('launch', '*.launch.py'))),
        (os.path.join('share', package_name, 'config'), glob(os.path.join('config', '*'))),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='ROS2 Learner',
    maintainer_email='learner@ros2.org',
    description='ROS2 Learning: TF2 coordinate frames and transforms',
    license='MIT',
    entry_points={
        'console_scripts': [
            'static_tf_node = learning_tf.static_tf_node:main',
            'dynamic_tf_node = learning_tf.dynamic_tf_node:main',
            'tf_listener_node = learning_tf.tf_listener_node:main',
        ],
    },
)
