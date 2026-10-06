from setuptools import find_packages, setup

package_name = 'quadruped_control'

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
    description='Low-level control for quadruped robot',
    license='MIT',
    entry_points={
        'console_scripts': [
            'whole_body_controller = quadruped_control.whole_body_controller:main',
            'joint_pd_controller = quadruped_control.joint_pd_controller:main',
        ],
    },
)
