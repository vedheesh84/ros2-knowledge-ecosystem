from setuptools import find_packages, setup

package_name = 'quadruped_locomotion'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='User',
    maintainer_email='user@example.com',
    description='Locomotion planning for quadruped robot',
    license='MIT',
    entry_points={
        'console_scripts': [
            'gait_scheduler = quadruped_locomotion.gait_scheduler:main',
            'swing_trajectory = quadruped_locomotion.swing_trajectory:main',
            'mpc_node = quadruped_locomotion.mpc_controller.mpc_node:main',
        ],
    },
)
