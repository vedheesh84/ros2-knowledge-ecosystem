from glob import glob
from setuptools import setup

package_name = "balancing_robot_description"

setup(
    name=package_name,
    version="0.1.0",
    packages=[package_name],
    data_files=[
        ("share/ament_index/resource_index/packages", [f"resource/{package_name}"]),
        (f"share/{package_name}", ["package.xml", "README.md"]),
        (f"share/{package_name}/meshes", glob("meshes/*")),
        (f"share/{package_name}/urdf", glob("urdf/*")),
        (f"share/{package_name}/launch", glob("launch/*.py")),
        (f"share/{package_name}/rviz", glob("rviz/*")),
        (f"lib/{package_name}", ["scripts/generate_balancing_robot_freecad.py"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="bhuvanesh",
    maintainer_email="bhuvanesh@todo.todo",
    description="FreeCAD-generated self-balancing two-wheel robot meshes and URDF description.",
    license="MIT",
    entry_points={
        "console_scripts": [],
    },
)
