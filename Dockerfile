# Use the official latest Python image as the base image

# Use the Miniconda3 image as the base image.
FROM frolvlad/alpine-miniconda3

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=UTF-8 \
    LD_LIBRARY_PATH=/usr/local/lib:/usr/local/lib64 \
    ENV RMR_SEED_RT=/app/ts-xapp/init/test_route.rt

# Install system dependencies
RUN apk --no-cache add \
    build-base \
    musl-dev \
    zlib-dev \
    wget \
    dpkg \
    git \
    lksctp-tools-dev

# RMR setup
RUN mkdir -p /app/route_mr/ /app/ts-xapp/init
COPY ts-xapp/init/test_route.rt /app/ts-xapp/init/test_route.rt

# copy rmr files from builder image in lieu of an Alpine package
COPY --from=nexus3.o-ran-sc.org:10002/o-ran-sc/bldr-alpine3-rmr:4.6.0 /usr/local/lib64/librmr* /usr/local/lib64/
COPY --from=nexus3.o-ran-sc.org:10002/o-ran-sc/bldr-alpine3-rmr:4.6.0 /usr/local/bin/rmr* /usr/local/bin/

# Set the working directory
WORKDIR /app/ts-xapp

# Copy the requirements.txt first, for separate dependency resolving and layering
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy the rest of the application code and dependencies into the container
COPY . .

# Expose the necessary ports
EXPOSE 8585
EXPOSE 8586
EXPOSE 3000
# Expose for ts-xapp and its dashboard
# Port 6000 is related to ts-xapp & Port 5000 is related to ts-xapp's API
# Port 5001 is related to ts-xapp's dashboard
EXPOSE 6000
EXPOSE 5000
EXPOSE 5001

# Set the default command to run when the container starts.
RUN python3 --version

# This will execute the TS-xApp.py script using Python.
CMD ["python3", "/app/ts-xapp/src/ts-xapp.py"]
