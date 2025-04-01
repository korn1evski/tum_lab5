from setuptools import setup, find_packages

setup(
    name="go2web",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "beautifulsoup4==4.12.3",
        "argparse==1.4.0",
    ],
    entry_points={
        "console_scripts": [
            "go2web=go2web:main",
        ],
    },
) 