from setuptools import setup, find_packages

setup(
    name="star_citizen_checkout",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
)
