from setuptools import setup

package_name = 'swarm_control'

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
    description='Position PID control and flight dynamics for swarm agents.',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'flight_controller_node = swarm_control.flight_controller_node:main',
        ],
    },
)
