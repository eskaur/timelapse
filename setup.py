"""Settings for building and installing package"""

import setuptools

with open("README.md", "r") as fh:
    LONG_DESCRIPTION = fh.read()

setuptools.setup(
    name="timelapse",
    version="0.1",
    author="Eskil Aursand",
    author_email="eskil.aursand@gmail.com",
    description="A small time-lapse creation library",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://github.com/eskaur/timelapse",
    packages=setuptools.find_packages(),
    install_requires=["numpy", "opencv-python"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    license="MIT",
)
