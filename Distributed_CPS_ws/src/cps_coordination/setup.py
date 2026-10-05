from setuptools import setup

package_name = 'cps_coordination'

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
    maintainer='Intelligent Systems Architecture Team',
    maintainer_email='developer@ecosystem.local',
    description='High-level distributed coordination, mission planning, and map fusion for multi-robot CPS.',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'base_coordinator_node = cps_coordination.base_coordinator_node:main',
            'map_merger_node = cps_coordination.map_merger_node:main',
            'cbba_auction_node = cps_coordination.cbba_auction_node:main',
            'peer_collision_avoidance = cps_coordination.peer_collision_avoidance:main',
            'health_watchdog_node = cps_coordination.health_watchdog_node:main',
        ],
    },
)
