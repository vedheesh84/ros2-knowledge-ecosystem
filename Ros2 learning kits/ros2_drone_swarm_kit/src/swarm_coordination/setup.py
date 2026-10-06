from setuptools import setup

package_name = 'swarm_coordination'

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
    description='Distributed area coverage, search-and-rescue partitioning, and swarm mission dispatch.',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'area_coverage_node = swarm_coordination.area_coverage_node:main',
            'dispatch_node = swarm_coordination.dispatch_node:main',
        ],
    },
)
