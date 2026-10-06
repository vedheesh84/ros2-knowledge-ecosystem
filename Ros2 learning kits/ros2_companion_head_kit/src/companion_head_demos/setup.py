from setuptools import setup

package_name = 'companion_head_demos'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name, package_name + '.breakers'],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Ved',
    maintainer_email='ved@example.com',
    description='Progressive demos for Companion Head robot',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            # Demos
            'demo_01_expressions = companion_head_demos.demo_01_expressions:main',
            'demo_02_servo_control = companion_head_demos.demo_02_servo_control:main',
            'demo_03_vision = companion_head_demos.demo_03_vision:main',
            'demo_04_audio = companion_head_demos.demo_04_audio:main',
            'demo_05_mood = companion_head_demos.demo_05_mood:main',
            'demo_06_multimodal = companion_head_demos.demo_06_multimodal:main',
            'demo_07_full_companion = companion_head_demos.demo_07_full_companion:main',
            # Breakers
            'break_camera = companion_head_demos.breakers.break_camera:main',
            'break_audio = companion_head_demos.breakers.break_audio:main',
            'break_servo = companion_head_demos.breakers.break_servo:main',
            'break_display = companion_head_demos.breakers.break_display:main',
        ],
    },
)
