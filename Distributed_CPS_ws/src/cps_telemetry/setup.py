from setuptools import setup
import os
from glob import glob

package_name = 'cps_telemetry'

setup(
    name=package_name,
    version='1.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'dashboards'), glob('dashboards/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Intelligent Systems Architecture Team',
    maintainer_email='developer@ecosystem.local',
    description='Metrics exporter and telemetry monitors for multi-robot CPS.',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'topic_delay_monitor = cps_telemetry.topic_delay_monitor:main',
            'prometheus_ros_exporter = cps_telemetry.prometheus_ros_exporter:main',
        ],
    },
)
