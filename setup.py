from setuptools import setup, find_packages
import os

# Read the content of the README.md file
def read_file(filename):
    with open(filename, 'r') as f:
        return f.read()

setup(
    name="TS-xApp",
    version="1.0.0",
    packages=find_packages(exclude=["tests.*", "tests"]),
    description="Traffic Steering xApp",
    long_description=read_file('README.md'),
    long_description_content_type="text/markdown",  # Specify the content type of the long description
    author='Milad Natanzi',
    author_email='snatanzi@wpi.edu',
    url="https://github.com/natanzi/TS-xApp",
    install_requires=[
        "ricxappframe>=1.1.1,<3.0.0", 
        "ricsdl==3.1.1", 
        "socket.py==0.1.0", 
        "APScheduler", 
        "thread6", 
        "redis", 
        "pandas>=1.1.3", 
        "joblib>=0.3.2", 
        "Scikit-learn>=0.21", 
        "schedule>=0.0.0", 
        "influxdb", 
        "p5py", 
        "PEP517", 
        "Cython", 
        "numpy >= 1.16.2", 
        "ipython", 
        "tensorflow", 
        "statistics", 
        "matplotlib", 
        "gym", 
        "pygame", 
        "typing", 
        "shapely", 
        "svgpath2mpl", 
        "abcplus", 
        "influxdb-client"
    ],
    python_requires='>=3.12',
    install_requires=["ricxappframe>=1.1.1,<3.2.3"],
    entry_points={"console_scripts": ["run-mr.py=mr.main:start"]},  # adds a magical entrypoint for Docker
    license="Apache 2.0",
    data_files=[("", ["LICENSE.txt"])],
)
