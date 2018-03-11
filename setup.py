#!/usr/bin/env python
from setuptools import setup

def readme():
    with open("README.rst") as f:
        return f.read()

setup(
    name="pyCBT",
    version="1.0.0-alpha",
    description="A bunch of tools for trading in FOREX.",
    long_description=readme(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License OSID approved :: MIT License",
        "Programming Language :: Python :: 2.7",
        "Topic :: Finances :: Data Analysis :: Machine Learning"
    ],
    keywords="finances FOREX analysis ML",
    url="https://github.com/ajmejia/python-cbt",
    author="Alfredo Mejia-Narvaez",
    author_email="alfredo.m.cbt@gmail.com",
    license="MIT",
    packages=["pyCBT"],
    install_requires=[
        "micropython-collections == 0.1.2",
        "micropython-collections.defaultdict == 0.3",
        "micropython-collections.deque == 0.1.3",
        "micropython-string == 0.1.1",
        "micropython-urllib == 0.0.0",
        "micropython-urllib.parse == 0.5.2",
        "micropython-urllib.urequest == 0.6",
        "numpy == 1.14.1",
        "oandapyV20 == 0.5.0",
        "pandas == 0.22.0",
        "python_dateutil == 2.6.1",
        "pytz == 2018.3",
        "ruamel.yaml == 0.15.35"
    ],
    include_package_data=True,
    zip_safe=False,
    test_suite="nose.collector",
    tests_require=["nose"],
    scripts=["bin/cbt-config"],
)
