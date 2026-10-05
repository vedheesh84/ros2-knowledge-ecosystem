from setuptools import setup
import os
from glob import glob

package_name = 'line_follower_v6_exploratory'

setup(
    name=package_name,
    version='1.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
        (os.path.join('share', package_name, 'urdf'), glob('urdf/*')),
        (os.path.join('share', package_name, 'config'), glob('config/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Intelligent Systems Architecture Team',
    maintainer_email='developer@ecosystem.local',
    description='Line Follower Evolution V6: Exploratory Autonomous Robot',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'frontier_explorer_node = line_follower_v6_exploratory.frontier_explorer_node:main',
        ],
    },
)
