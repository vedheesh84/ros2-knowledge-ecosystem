from setuptools import setup

package_name = 'swarm_formation'

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
    description='Geometric formation flight engines for aerial swarms.',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'leader_follower_node = swarm_formation.leader_follower_node:main',
            'formation_manager_node = swarm_formation.formation_manager_node:main',
        ],
    },
)
