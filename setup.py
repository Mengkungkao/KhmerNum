"""
Setup configuration for KhmerNum package
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="khmernum",
    version="0.1.0",
    author="Mengkungkao",
    author_email="mengkungkao@gmail.com",
    description="Khmer Number Identifier - A pygame-based application",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mengkungkao/KhmerNum",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.13",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Education",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pygame>=2.0.0",
    ],
    entry_points={
        "console_scripts": [
            "khmernum=khmernum.app:main",
        ],
    },
)
