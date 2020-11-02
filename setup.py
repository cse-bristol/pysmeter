import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="pysmeter",
    version="1.0.0",
    author="Mark Gibbons",
    author_email="mark.gibbons@cse.org.uk",
    description="A package for predicting the HTC of a building using smart meter data.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cse-bristol/pysmeter",
    packages=setuptools.find_packages(),
    scripts=["bin/pysmeter"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        "tensorflow<2",
        "numpy",
        "requests"
    ]
)
