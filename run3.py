#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ASE–VASP run script
- Reads structure from restart.json
- Runs ionic relaxation using VASP via ASE
- Supports automatic restart if WAVECAR/CONTCAR exists
"""

import os
import subprocess

from ase.io import read, write
from ase.calculators.vasp import Vasp
from ase.calculators.calculator import CalculationFailed

name = "TRAINING"

# =========================
# 0) Safety checks
# =========================
if not os.path.isfile("restart.json"):
    raise FileNotFoundError("restart.json not found in the current directory.")

atoms = read("restart.json")

# Save initial structure for reference
write(f"{name}_init.traj", atoms)
write(f"{name}_init.cif", atoms)

print("===================================")
print("ASE–VASP calculation started")
print("PWD:", os.getcwd())
print("VASP_COMMAND:", os.environ.get("VASP_COMMAND", "NOT SET"))
print("VASP_PP_PATH:", os.environ.get("VASP_PP_PATH", "NOT SET"))
print("===================================")

# =========================
# 1) Restart logic
# =========================
has_wavecar = os.path.isfile("WAVECAR") and os.path.getsize("WAVECAR") > 0
has_contcar = os.path.isfile("CONTCAR") and os.path.getsize("CONTCAR") > 0

istart_val = 1 if (has_wavecar or has_contcar) else 0
icharg_val = 0

print(f"Restart flags: WAVECAR={has_wavecar}, CONTCAR={has_contcar}")
print(f"Using ISTART={istart_val}, ICHARG={icharg_val}")

# =========================
# 2) VASP calculator
# =========================
vasp_cmd = os.environ.get("VASP_COMMAND", "vasp_std")

calc = Vasp(
    command=vasp_cmd,

    istart=istart_val,
    icharg=icharg_val,

    encut=500,
    xc="PBE",
    gga="PE",

    # k-points for slab
    kpts=(5, 5, 5),
    gamma=True,

    # parallelization (disable if problematic)
    kpar=4,
    npar=16,

    # electronic settings
    ismear=0,
    sigma=0.05,
    nelm=500,
    algo="normal",
    ediff=1e-5,

    # ionic relaxation
    ibrion=2,
    isif=2,
    nsw=500,
    ediffg=-0.02,

    # misc
    prec="Normal",
    ispin=2,
    lwave=False,
    lvtot=False,
    lorbit=11,
    ivdw=0,

    # DFT+U
    ldautype=2,
    lasph=True,
    ldau_luj={
        "Ti": {"L": 2, "U": 3.00, "J": 0.0},
        "V":  {"L": 2, "U": 3.25, "J": 0.0},
        "Cr": {"L": 2, "U": 3.5,  "J": 0.0},
        "Mn": {"L": 2, "U": 3.75, "J": 0.0},
        "Fe": {"L": 2, "U": 4.3,  "J": 0.0},
        "Co": {"L": 2, "U": 3.32, "J": 0.0},
        "Ni": {"L": 2, "U": 5.50, "J": 0.0},
        "Cu": {"L": 2, "U": 3.0,  "J": 0.0},
        "Mo": {"L": 2, "U": 4.38, "J": 0.0},
        "W":  {"L": 2, "U": 6.2,  "J": 0.0},
        "Ce": {"L": 3, "U": 4.50, "J": 0.0},
        "O":  {"L": -1, "U": 0.0, "J": 0.0},
        "C":  {"L": -1, "U": 0.0, "J": 0.0},
        "Au": {"L": -1, "U": 0.0, "J": 0.0},
        "Ir": {"L": -1, "U": 0.0, "J": 0.0},
        "H":  {"L": -1, "U": 0.0, "J": 0.0},
        "N":  {"L": -1, "U": 0.0, "J": 0.0},
    },
    ldauprint=2,
    lmaxmix=6,
    lreal="Auto",

    # dipole correction for slab
    idipol=3,
    dipol=(0.5, 0.5, 0.5),
    ldipol=True,
)

atoms.calc = calc

# =========================
# 3) Run calculation
# =========================
try:
    energy = atoms.get_potential_energy()
    print("Total energy (eV):", energy)
except CalculationFailed as err:
    print("ERROR: ASE/VASP calculation failed.")
    raise err

# =========================
# 4) Save final structure
# =========================
if os.path.isfile("vasprun.xml"):
    try:
        final_atoms = read("vasprun.xml")
    except Exception:
        final_atoms = atoms
else:
    final_atoms = atoms

write("final_with_calculator.traj", final_atoms)
write("final_with_calculator.cif", final_atoms)

# Optional conversions
try:
    subprocess.check_call(
        "ase convert -f final_with_calculator.traj final_with_calculator.json",
        shell=True,
    )
except Exception:
    print("WARNING: failed to convert final_with_calculator.traj to json")

try:
    if os.path.isfile("OUTCAR"):
        subprocess.check_call(
            "ase convert -f OUTCAR full_relax.json",
            shell=True,
        )
except Exception:
    print("WARNING: failed to convert OUTCAR to json")

print("ASE–VASP calculation finished successfully.")
