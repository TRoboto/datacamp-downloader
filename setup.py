from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    required = fh.read().splitlines()

setup(
    name="datacamp-downloader",
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
    install_requires=required,
    setup_requires=["setuptools-git"],
    packages=find_packages(where="src"),
    package_data={"datacamp_downloader": ["*", "*/*", "*/*/*"]},
    python_requires=">=3.6",
    entry_points={"console_scripts": ["datacamp=datacamp_downloader.downloader:app"]},
)