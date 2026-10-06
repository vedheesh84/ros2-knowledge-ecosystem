import os
from glob import glob
from setuptools import setup

package_name = 'reef_drone_hardware'

setup(
    name=package_name,
    version='1.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Ved',
    maintainer_email='info@vedheesh.org',
    description='Serial hardware bridge for Reef Drone AUV',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'flight_bridge_node = reef_drone_hardware.flight_bridge_node:main',
        ],
    },
)
