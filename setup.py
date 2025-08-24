#!/usr/bin/env python3
"""
WebSocket Probe Tool - Setup Configuration
"""

from setuptools import setup, find_packages
import os

# 读取README文件
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# 读取requirements文件
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="websocket-probe",
    version="1.0.0",
    author="WebSocket Probe Tool Contributors",
    author_email="your-email@example.com",
    description="A comprehensive WebSocket connection probe and monitoring tool",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/websocket-probe",
    project_urls={
        "Bug Reports": "https://github.com/your-username/websocket-probe/issues",
        "Source": "https://github.com/your-username/websocket-probe",
        "Documentation": "https://github.com/your-username/websocket-probe/tree/main/docs",
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP :: WebSockets",
        "Topic :: Software Development :: Testing",
        "Topic :: System :: Monitoring",
        "Topic :: Utilities",
    ],
    python_requires=">=3.7",
    py_modules=["websocket_probe", "websocket_probe_py36"],
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-asyncio>=0.18.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
        "build": [
            "pyinstaller>=4.0",
            "setuptools>=45.0",
            "wheel>=0.37.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "websocket-probe=websocket_probe:main",
        ],
    },
    keywords="websocket, probe, testing, monitoring, network, http",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    platforms=["any"],
)
