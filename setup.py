import os
import modified

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


def get_description():
    f = open(os.path.abspath(os.path.join(os.path.dirname(__file__), 'README.md')), 'r')
    try:
        return f.read()
    finally:
        f.close()


setup(
    name="modified",
    version=modified.__version__,
    description="Python file modification tracker",
    long_description=get_description(),
    author="Scott Maxwell",
    author_email="scott@codecobblers.com",
    url=modified.__project_url__,
    license="MIT",
    py_modules=["modified"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
