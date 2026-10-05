from setuptools import setup

package_name = 'reef_drone_demos'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name, package_name + '.breakers'],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Ved',
    maintainer_email='ved@example.com',
    description='Progressive demos and failure injection for Reef Drone AUV',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'demo_01_buoyancy = reef_drone_demos.demo_01_buoyancy:main',
            'demo_02_thruster_control = reef_drone_demos.demo_02_thruster_control:main',
            'demo_03_depth_hold = reef_drone_demos.demo_03_depth_hold:main',
            'demo_04_heading_control = reef_drone_demos.demo_04_heading_control:main',
            'demo_05_station_keeping = reef_drone_demos.demo_05_station_keeping:main',
            'demo_06_waypoint_nav = reef_drone_demos.demo_06_waypoint_nav:main',
            'demo_07_survey_mission = reef_drone_demos.demo_07_survey_mission:main',
            'break_thruster = reef_drone_demos.breakers.break_thruster:main',
            'break_dvl = reef_drone_demos.breakers.break_dvl:main',
            'break_depth = reef_drone_demos.breakers.break_depth:main',
            'break_imu = reef_drone_demos.breakers.break_imu:main',
            'break_current = reef_drone_demos.breakers.break_current:main',
        ],
    },
)
