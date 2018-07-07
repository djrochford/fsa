import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="toc",
    version="0.0.1",
    author="Damien Rochford",
    author_email="djrochford@gmail.com",
    description="A package for doing theory-of-computation related stuff.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/djrochford/toc",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)