# Use the Miniconda3 image as the base image. Miniconda is a minimal installer for Conda, a package manager for Python.
FROM ubuntu
RUN apt-get update       
RUN apt-get install --assume-yes git
FROM continuumio/miniconda3
FROM python:3.12-rc-slim



# RMR setup
RUN mkdir -p /opt/route_mr/

# copy rmr files from builder image in lieu of an Alpine package
COPY --from=nexus3.o-ran-sc.org:10002/o-ran-sc/bldr-alpine3-rmr:4.0.5 /usr/local/lib64/librmr* /usr/local/lib64/

COPY --from=nexus3.o-ran-sc.org:10002/o-ran-sc/bldr-alpine3-rmr:4.0.5 /usr/local/bin/rmr* /usr/local/bin/
ENV LD_LIBRARY_PATH /usr/local/lib/:/usr/local/lib64
COPY local.rt /opt/route_mr/local.rt
ENV RMR_SEED_RT /opt/route_mr/local.rt

# Update the package list and install necessary system libraries and tools.
# These libraries might be dependencies for some Python packages or required for certain system operations.
RUN apt-get update && apt-get -y install build-essential musl-dev libjpeg-dev zlib1g-dev libgl1-mesa-dev wget dpkg git libsctp-dev

# Copy all files from the current directory on the host to the /tmp/ml directory inside the Docker container.
# This is useful for transferring your application code and dependencies into the container.
COPY . /tmp/TS-xApp

# Set the working directory inside the container to /tmp/ml.
# All subsequent commands will be run from this directory.
# Go to /tmp/TS-xApp
WORKDIR /tmp/TS-xApp

# Upgrade pip to the latest version and then install the Python packages listed in requirements.txt.
# The -r flag is used to specify that pip should install packages from the provided requirements file.
RUN pip install --upgrade pip && pip install -r requirements.txt

# Set an environment variable to ensure Python runs in unbuffered mode.
# This is useful in containerized environments to make sure that logs and print statements are immediately visible.
ENV PYTHONUNBUFFERED 1

EXPOSE 8585
EXPOSE 8586
EXPOSE 3000
EXPOSE 5000

# Set the default command to run when the container starts.
# This will execute the TS-xApp.py script using Python.
CMD ["python", "TS-xApp.py"]
