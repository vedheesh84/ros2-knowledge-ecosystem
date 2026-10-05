from setuptools import setup

package_name = 'reef_drone_control'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/config', ['config/control.yaml']),
        ('share/' + package_name + '/launch', ['launch/control.launch.py']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Ved',
    maintainer_email='ved@example.com',
    description='Control nodes for Reef Drone AUV',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'thruster_allocator = reef_drone_control.thruster_allocator:main',
            'depth_controller = reef_drone_control.depth_controller:main',
            'heading_controller = reef_drone_control.heading_controller:main',
            'velocity_controller = reef_drone_control.velocity_controller:main',
            'station_keeping = reef_drone_control.station_keeping:main',
        ],
    },
)
