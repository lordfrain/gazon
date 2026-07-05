from setuptools import find_packages, setup

package_name = 'mower_safety'

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/safety_demo.launch.py']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='anton',
    maintainer_email='anton.cat.anton@gmail.com',
    description='Safety watchdog and fake lidar publisher for the autonomous lawn mower project',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'fake_lidar_publisher = mower_safety.fake_lidar_publisher:main',
            'safety_watchdog = mower_safety.safety_watchdog:main',
            'cmd_vel_gate = mower_safety.cmd_vel_gate:main',
        ],
    },
)
