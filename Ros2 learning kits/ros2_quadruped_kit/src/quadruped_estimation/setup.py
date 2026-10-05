from setuptools import find_packages, setup

package_name = 'quadruped_estimation'

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
    description='State estimation for quadruped robot',
    license='MIT',
    entry_points={
        'console_scripts': [
            'state_estimator = quadruped_estimation.state_estimator:main',
            'contact_estimator = quadruped_estimation.contact_estimator:main',
        ],
    },
)
