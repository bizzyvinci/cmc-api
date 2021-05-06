from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="cmc-api",
    version="0.0.1",
    author="Bisola Olasehinde",
    author_email="horlasehinde@gmail.com",
    description="Unofficial wrapper for coinmarketcap api",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license = "MIT",
    url="https://github.com/bizzyvinci/cmc-api",
    packages=["cmc_api"],
    keywords = ["coinmarketcap", "cmc", "API", "crypto", "cryptocurrency"],
    install_requires=[
        'requests'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3',
)
