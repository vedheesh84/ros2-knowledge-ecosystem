from setuptools import setup
import os
from glob import glob

package_name = 'arm_kinematics'

setup(
    name=package_name,
    version='1.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools', 'numpy'],
    zip_safe=True,
    maintainer='Vedheesh B',
    maintainer_email='vedheesh@intelligentsystems.io',
    description='Analytical kinematics solver for robotic arm.',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'kinematics_service_node = arm_kinematics.kinematics_service_node:main',
        ],
    },
)
