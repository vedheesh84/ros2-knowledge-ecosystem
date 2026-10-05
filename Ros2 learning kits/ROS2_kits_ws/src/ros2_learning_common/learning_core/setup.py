"""
Setup configuration for the learning_core package.

This file tells Python and ROS2 how to install this package.
Key concepts demonstrated:
- Package discovery with find_packages()
- Data files for launch and config
- Entry points mapping executables to Python functions
"""

from setuptools import find_packages, setup
import os
from glob import glob

# The package name must match the directory name and package.xml
package_name = 'learning_core'

setup(
    # =========================================================================
    # PACKAGE METADATA
    # =========================================================================
    # These fields describe the package for PyPI and ROS2 tooling

    name=package_name,
    version='1.0.0',

    # find_packages() automatically discovers Python packages (directories with __init__.py)
    # exclude=['test'] prevents test directories from being installed
    packages=find_packages(exclude=['test']),

    # =========================================================================
    # DATA FILES
    # =========================================================================
    # These files are installed to the share directory, NOT the Python path
    # This is how ROS2 finds launch files, configs, etc.

    data_files=[
        # Register this package with ament index (required for ros2 run to work)
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),

        # Install package.xml (required for ROS2 tooling)
        ('share/' + package_name, ['package.xml']),

        # Install launch files to share/<package>/launch/
        (os.path.join('share', package_name, 'launch'),
            glob(os.path.join('launch', '*.launch.py'))),

        # Install config files to share/<package>/config/
        (os.path.join('share', package_name, 'config'),
            glob(os.path.join('config', '*.yaml'))),
    ],

    # =========================================================================
    # INSTALLATION REQUIREMENTS
    # =========================================================================

    install_requires=['setuptools'],
    zip_safe=True,

    # =========================================================================
    # PACKAGE INFORMATION
    # =========================================================================

    maintainer='ROS2 Learner',
    maintainer_email='learner@ros2.org',
    description='ROS2 Learning: Core concepts - nodes, graph, parameters',
    license='MIT',

    # =========================================================================
    # TESTING
    # =========================================================================

    tests_require=['pytest'],

    # =========================================================================
    # ENTRY POINTS (CRITICAL!)
    # =========================================================================
    # This maps executable names to Python functions.
    # Format: 'executable_name = package.module:function'
    #
    # When you run: ros2 run learning_core hello_node
    # ROS2 looks up 'hello_node' here and calls learning_core.hello_node:main()

    entry_points={
        'console_scripts': [
            # Format: 'ros2_executable = python_package.module:function'
            'hello_node = learning_core.hello_node:main',
            'graph_introspector_node = learning_core.graph_introspector_node:main',
            'parameter_echo_node = learning_core.parameter_echo_node:main',
        ],
    },
)
