from setuptools import setup, find_packages

setup(
    name="tv-control-center",
    version="0.0.1",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "bravia_control": ["static/*"],
    },
    entry_points={
        "console_scripts": [
            "tv-control-center=bravia_control.cli:main",
            "bravia-control=bravia_control.cli:main",
        ],
    },
)
