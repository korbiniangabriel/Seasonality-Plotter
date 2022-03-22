import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Seasonality Plotter",
    version="1.0.0",
    author="Korbinian Gabriel",
    description="This script contains a seasonality plotter. The plotter takes in different time frames and plots the seasonality of a wished asset.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/korbiniangabriel/Seasonality-Plotter",
    project_urls={
        "Bug Tracker": "https://github.com/korbiniangabriel/Seasonality-Plotter/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)