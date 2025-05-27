from setuptools import setup, find_packages
from pathlib import Path

# Read long description from README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="star_citizen_checkout",
    version="0.1.0",
    description="Star Citizen Checkout Bot",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Star Citizen Bot Team",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.9",
    install_requires=[
        "selenium>=4.11.0",
        "webdriver-manager>=4.0.0",
        "requests>=2.31.0",
        "colorama>=0.4.6",
    ],
    entry_points={
        "console_scripts": [
            "star-citizen-bot=star_citizen_checkout.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Internet :: WWW/HTTP :: Browsers",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
