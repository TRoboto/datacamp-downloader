import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="datacamp-downloader",  # Replace with your own username
    version="2.0",
    author="Mohammad Al-Fetyani",
    author_email="m4bh@hotmail.com",
    description="Download your completed courses on Datacamp easily!",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TRoboto/datacamp-downloader",
    project_urls={
        "Bug Tracker": "https://github.com/TRoboto/datacamp-downloader/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
    entry_points={"console_scripts": ["datacamp=datacamp_downloader.downloader:main"]},
)