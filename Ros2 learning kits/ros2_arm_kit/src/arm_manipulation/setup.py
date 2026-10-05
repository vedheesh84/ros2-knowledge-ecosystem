from setuptools import setup
import os

package_name = 'arm_manipulation'

setup(
    name=package_name,
    version='1.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Vedheesh B',
    maintainer_email='vedheesh@intelligentsystems.io',
    description='Autonomous manipulation state machine and gripper action execution.',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'gripper_action_server = arm_manipulation.gripper_action_server:main',
            'pick_place_state_machine = arm_manipulation.pick_place_state_machine:main',
        ],
    },
)
