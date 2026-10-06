from setuptools import find_packages, setup

package_name = 'quadruped_behaviors'

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
    description='Behavior state machine for quadruped',
    license='MIT',
    entry_points={
        'console_scripts': [
            'behavior_state_machine = quadruped_behaviors.behavior_state_machine:main',
        ],
    },
)
