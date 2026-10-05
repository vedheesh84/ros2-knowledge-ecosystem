from setuptools import setup

package_name = 'swarm_demos'

setup(
    name=package_name,
    version='1.0.0',
    packages=[package_name, package_name + '.breakers'],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Vedheesh B',
    maintainer_email='vedheesh@intelligentsystems.io',
    description='Progressive multi-agent swarm demos and breakers.',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'demo_01_single_drone_flight = swarm_demos.demo_01_single_drone_flight:main',
            'demo_02_multi_drone_namespacing = swarm_demos.demo_02_multi_drone_namespacing:main',
            'demo_03_leader_follower = swarm_demos.demo_03_leader_follower:main',
            'demo_04_dynamic_formation = swarm_demos.demo_04_dynamic_formation:main',
            'demo_05_collision_avoidance = swarm_demos.demo_05_collision_avoidance:main',
            'demo_06_swarm_area_coverage = swarm_demos.demo_06_swarm_area_coverage:main',
            'break_communication_drop = swarm_demos.breakers.break_communication_drop:main',
            'break_leader_failure = swarm_demos.breakers.break_leader_failure:main',
            'break_gps_drift = swarm_demos.breakers.break_gps_drift:main',
            'break_swarm_collision = swarm_demos.breakers.break_swarm_collision:main',
        ],
    },
)
