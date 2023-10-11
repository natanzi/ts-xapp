from setuptools import setup, find_packages
import os

def read_file(filename):
    with open(os.path.join(os.path.dirname(__file__), filename), 'r') as file:
        return file.read()

setup(
    name="TS-xApp",
    version="1.0.0",
    packages=find_packages(exclude=["tests.*", "tests"]),
    description="Traffic Steering xApp",
    long_description=read_file('README.md'),
    long_description_content_type="text/markdown",
    author='Milad Natanzi',
    author_email='snatanzi@wpi.edu',
    url="https://github.com/natanzi/TS-xApp",
    install_requires=[
        "ricxappframe>=1.1.1", 
        "ricsdl==3.1.1", 
        "socket.py==0.1.0", 
        "APScheduler", 
        "thread6", 
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
    python_requires='>=3.8',  # Adjust this as necessary
    entry_points={
        "console_scripts": [
            "ts-xapp=src.TS_xApp:main",  # This tells setuptools to create a script that runs src.TS_xApp.main()
        ]
    },
    license="Apache 2.0",
    data_files=[("", ["LICENSE.txt"])],
)
