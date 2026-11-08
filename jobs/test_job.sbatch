#!/bin/bash
#SBATCH --job-name=test_mpi
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=2
#SBATCH --output=slurm_output_%j.log

echo "Starting containerized MPI job on nodes: $SLURM_JOB_NODELIST"

# Run the docker container using host networking
docker run --rm --net=host desktop-grid-mpi:v1