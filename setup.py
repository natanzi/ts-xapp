from setuptools import setup, find_packages
import os

def read_file(filename):
    with open(os.path.join(os.path.dirname(__file__), filename), 'r', encoding='utf-8') as file:  # specify the encoding
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
    url="https://github.com/natanzi/ts-xApp",
    install_requires=[
        "wheel",
        "ricxappframe>=1.1.1", 
        "ricsdl==3.1.3", 
        "socket.py", 
        "APScheduler", 
        "thread6", 
        "pandas", 
        "joblib", 
        "influxdb", 
        "numpy", 
        "influxdb-client",
        "flask"
    ],
    python_requires='==3.11.5',  
    entry_points={
        "console_scripts": [
            "ts-xapp=src.ts_xApp:main",  # This tells setuptools to create a script that runs src.TS_xApp.main()
        ]
    },
    license="Apache 2.0",
    data_files=[("", ["LICENSE.txt"])],
)
