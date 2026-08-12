#!/usr/bin/env bash
#SBATCH -J file_name
#SBATCH -p all
#SBATCH -N 1
#SBATCH --nodelist=node00xx (xx = replace with an empty node (idle))
#SBATCH --ntasks-per-node=64
#SBATCH --time=2-00:00:00
#SBATCH --hint=nomultithread
#SBATCH --output=vasp.out
#SBATCH --error=vasp.err

set -euo pipefail
echo "Job started on $(date)"
echo "Job ID: $SLURM_JOB_ID"
echo "PWD: $(pwd)"

module purge
module load vasp/6.5.0-cpu-ompi-intel1api
module load intel-oneapi-mkl/2025.2
module load intel-oneapi/2025.2.lua
module load conda/25.08
module load ase/3.23.0

ulimit -s unlimited


export OMP_NUM_THREADS=1

export VASP_COMMAND="srun --mpi=pmix -n ${SLURM_NTASKS} vasp_std"
#export VASP_COMMAND="srun -n ${SLURM_NTASKS} vasp_std"

export VASP_PP_PATH=/home/g202425580
echo "VASP_COMMAND=$VASP_COMMAND"
echo "VASP_PP_PATH=$VASP_PP_PATH"

python -u ./run3.py
