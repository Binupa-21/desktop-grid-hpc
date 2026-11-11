FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

# 1. Install build tools, OpenMPI, and OpenBLAS
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    gfortran \
    openmpi-bin \
    libopenmpi-dev \
    libopenblas-dev \
    python3 \
    python3-pip \
    wget \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# 2. Copy and compile sample MPI program
COPY mpi_hello.c /workspace/
RUN mpicc -o mpi_hello mpi_hello.c

# 3. Download and build HPL using native mpicc wrappers and OpenBLAS
RUN wget https://www.netlib.org/benchmark/hpl/hpl-2.3.tar.gz && \
    tar -zxf hpl-2.3.tar.gz && \
    cd hpl-2.3 && \
    cp setup/Make.Linux_PII_CBLAS Make.linux && \
    sed -i 's|^ARCH *=.*|ARCH = linux|' Make.linux && \
    sed -i 's|^TOPdir *=.*|TOPdir = /workspace/hpl-2.3|' Make.linux && \
    sed -i 's|^MPdir *=.*|MPdir =|' Make.linux && \
    sed -i 's|^MPinc *=.*|MPinc =|' Make.linux && \
    sed -i 's|^MPlib *=.*|MPlib =|' Make.linux && \
    sed -i 's|^LAdir *=.*|LAdir =|' Make.linux && \
    sed -i 's|^LAinc *=.*|LAinc =|' Make.linux && \
    sed -i 's|^LAlib *=.*|LAlib = -lopenblas|' Make.linux && \
    sed -i 's|^CC *=.*|CC = mpicc|' Make.linux && \
    sed -i 's|^LINKER *=.*|LINKER = mpicc|' Make.linux && \
    make arch=linux && \
    cp bin/linux/xhpl /usr/local/bin/xhpl && \
    cd /workspace && rm -rf hpl-2.3*

CMD ["mpirun", "--allow-run-as-root", "-np", "2", "/workspace/mpi_hello"]