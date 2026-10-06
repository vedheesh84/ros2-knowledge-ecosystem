import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'quadruped_demos'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'),
            glob('launch/*.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='User',
    maintainer_email='user@example.com',
    description='Progressive demos for quadruped learning',
    license='MIT',
    entry_points={
        'console_scripts': [
            'demo_01_joint_control = quadruped_demos.demo_01_joint_control:main',
            'demo_02_leg_kinematics = quadruped_demos.demo_02_leg_kinematics:main',
            'demo_03_standing = quadruped_demos.demo_03_standing:main',
            'demo_04_weight_shifting = quadruped_demos.demo_04_weight_shifting:main',
            'demo_05_walking = quadruped_demos.demo_05_walking:main',
            'demo_06_trotting = quadruped_demos.demo_06_trotting:main',
            'demo_07_disturbance = quadruped_demos.demo_07_disturbance:main',
            'break_imu = quadruped_demos.breakers.break_imu:main',
            'break_contact = quadruped_demos.breakers.break_contact:main',
            'break_gait = quadruped_demos.breakers.break_gait:main',
        ],
    },
)
