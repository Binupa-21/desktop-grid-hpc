FROM ubuntu:24.04

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install essential build tools, OpenMPI, and Python
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    gfortran \
    openmpi-bin \
    libopenmpi-dev \
    hpl-openmpi \

    python3 \
    python3-pip \
    wget \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Compile a sample MPI program on build
COPY mpi_hello.c /workspace/
RUN mpicc -o mpi_hello mpi_hello.c

CMD ["mpirun", "--allow-run-as-root", "-np", "2", "/workspace/mpi_hello"]