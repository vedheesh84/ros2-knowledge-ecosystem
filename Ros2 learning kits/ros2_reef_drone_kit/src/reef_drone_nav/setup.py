from setuptools import setup

package_name = 'reef_drone_nav'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/config', ['config/nav.yaml']),
        ('share/' + package_name + '/launch', ['launch/nav.launch.py']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Ved',
    maintainer_email='ved@example.com',
    description='Navigation for Reef Drone AUV',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'waypoint_follower = reef_drone_nav.waypoint_follower:main',
            'mission_executor = reef_drone_nav.mission_executor:main',
        ],
    },
)
