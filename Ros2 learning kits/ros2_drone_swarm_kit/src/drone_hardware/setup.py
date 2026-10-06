import os
from glob import glob
from setuptools import setup

package_name = 'drone_hardware'

setup(
    name=package_name,
    version='1.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Vedheesh B',
    maintainer_email='vedheesh@intelligentsystems.io',
    description='Serial telemetry and control bridge connecting ROS 2 to physical and simulated flight controllers.',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'flight_controller_bridge = drone_hardware.flight_controller_bridge:main',
        ],
    },
)
