from setuptools import setup
import os
from glob import glob

package_name = 'companion_head_expression'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Ved',
    maintainer_email='ved@example.com',
    description='Face display and expression system for Companion Head',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'expression_renderer = companion_head_expression.expression_renderer:main',
        ],
    },
)
