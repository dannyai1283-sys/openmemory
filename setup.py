from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="openmemory",
    version="0.1.0",
    author="OpenMemory Team",
    author_email="contact@openmemory.ai",
    description="Universal Memory Layer for AI Agents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/openmemory/openmemory",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.20.0",
        "faiss-cpu>=1.7.0",
    ],
    extras_require={
        "embeddings": [
            "sentence-transformers>=2.2.0",
        ],
        "redis": [
            "redis>=4.0.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=0.950",
        ],
        "docs": [
            "mkdocs>=1.4.0",
            "mkdocs-material>=8.5.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "openmemory=openmemory.cli:main",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/openmemory/openmemory/issues",
        "Source": "https://github.com/openmemory/openmemory",
        "Documentation": "https://openmemory.readthedocs.io",
    },
)
