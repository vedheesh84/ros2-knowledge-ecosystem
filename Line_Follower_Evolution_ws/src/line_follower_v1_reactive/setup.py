from setuptools import setup
import os
from glob import glob

package_name = 'line_follower_v1_reactive'

setup(
    name=package_name,
    version='1.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
        (os.path.join('share', package_name, 'urdf'), glob('urdf/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Intelligent Systems Architecture Team',
    maintainer_email='developer@ecosystem.local',
    description='Line Follower Evolution V1: Baseline Reactive Tracker',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'reactive_threshold_node = line_follower_v1_reactive.reactive_threshold_node:main',
            'simulated_track_sensor = line_follower_v1_reactive.simulated_track_sensor:main',
        ],
    },
)
