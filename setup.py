from setuptools import setup, find_packages

setup(
    name="tv-control-center",
    version="0.0.2",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "tv_control_center": ["static/*"],
    },
    entry_points={
        "console_scripts": [
            "tv-control-center=tv_control_center.cli:main",
        ],
    },
)
