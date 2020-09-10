import setuptools
from pathlib import Path

project_dir = Path(__file__).resolve().parent

long_description = (project_dir / "README.md").read_text()
install_requires = (project_dir / "requirements.txt").read_text().split("\n")


setuptools.setup(
    name="reven2-ltrace",
    version="0.0.1",
    author="Tetrane",
    author_email="contact@tetrane.com",
    description="ltrace-like script for REVEN",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://www.tetrane.com",
    license="MIT",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux ",
    ],
    include_package_data=True,
    python_requires=">=3.5.3",
    install_requires=install_requires,
    entry_points={
        "console_scripts": ["reven2-ltrace=reven2_ltrace.ltrace:main"]
    },
)
