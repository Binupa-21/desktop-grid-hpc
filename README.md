# Automated Desktop-Grid HPC Cluster Using Idle Academic Computer Labs
CO3563 High Performance Computing Project · B. A. B. N. Ariyarathna (EN113753) · Supervisor: Dr. Chinthaka Kumara

## What it does
Turns idle lab PCs into an on-demand HPC cluster using Slurm, Docker and an idle-detection daemon,
and measures how well it scales on Gigabit Ethernet.

## Status
Proposal stage. The scripts are drafts and have not yet been tested on the lab cluster.

## Components
daemon/ (idle detection and eviction), slurm/ (config and epilog), docker/ (benchmark image),
jobs/ (example job scripts), docs/ (report and slides).

## Setup and run
1. Install Ubuntu packages: `sudo apt install python3-evdev python3-psutil` (version to be confirmed)
2. ... (add step by step as you build them)

## Results
(Link to results/ when available.)

## Generative AI
See AI_USAGE.md.