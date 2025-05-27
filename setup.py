from setuptools import setup, find_packages

setup(
    name="star_citizen_checkout",
    version="0.1.0",
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
            "star-citizen-bot=star_citizen_checkout.bot:main",
        ],
    },
)
