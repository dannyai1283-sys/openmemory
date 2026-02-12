from setuptools import setup, find_packages

setup(
    name="ocmem",
    version="0.1.0",
    description="OpenClaw Memory System - A mem0-inspired memory layer for AI Agents",
    author="OpenClaw Team",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.20.0",
        "faiss-cpu>=1.7.0",
        "sentence-transformers>=2.2.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "mypy>=0.950",
        ]
    },
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "ocmem=ocmem.cli:main",
        ]
    },
)
