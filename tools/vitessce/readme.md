# Spatial Transcriptomics Dashboard

This repository provides a pipeline to transform raw spatial transcriptomics data (.h5ad format) into interactive Vitessce visualizations, with full data lineage and metadata management powered by LaminDB.

🚀 Quick Start (From Scratch)
1. Prerequisites

    Docker and Docker Compose installed.

    Place your raw data files (.h5ad) into the following directory: /data/script01_adatas/

2. Launching the Environment

From the project root, build and start the containers:
Bash

docker-compose up --build -d

    Note: The container is configured to start as root to automatically fix folder permissions for the data/ directory, ensuring SQLite and Zarr writers have full access.

🧬 Data Pipeline

Follow the notebooks in numerical order to process the data:
[010] Convert-h5ad-To-Zarr

Purpose: Web-optimization and format conversion.

    Reads raw .h5ad files.

    Cleans metadata and converts categorical columns to strings (required for Vitessce compatibility).

    Exports Zarr V2 folders with consolidated metadata into /data/script01_zarrs/.

[011] Init_LaminDB

Purpose: Data indexing and traceability.

    Initializes the local LaminDB instance.

    Indexes the Zarr files created in the previous step as "Artifacts".

    Links metadata (Patient_ID, Tumor_Status, Region) using ULabels to enable advanced filtering in the dashboard.

[020] Launch-Vitessce_Over_LaminDB

Purpose: Single-sample spatial explorer.

    Features an interactive UI with dropdown menus (Status → Patient → Sample).

    Dynamically fetches the requested Artifact from LaminDB and renders the Vitessce widget.

    Integrated views: Spatial Map, UMAP, Cell Sets, Feature List, and Heatmap.

[030] Compare_2Patients

Purpose: Comparative analysis.

    Allows the user to select and display two different samples side-by-side.

    Ideal for comparing spatial structures between "Hot" vs "Cold" tumors or different patients.

🛠 Project Structure
Plaintext

.
├── docker-compose.yml        # Docker config (User root + automated permission fix)
├── jupyter/
│   └── Dockerfile            # Custom image (Scanpy, LaminDB, Vitessce)
├── data/
│   ├── script01_adatas/      # Input: Raw .h5ad files
│   ├── script01_zarrs/       # Output: Web-ready .zarr files (V2)
│   └── lamin_storage/        # Internal LaminDB database & storage
└── jupyter/notebooks/        # The 4 pipeline notebooks

⚠️ Technical Notes

    Permissions: If you encounter an OperationalError: attempt to write a readonly database, simply restart the stack with docker-compose up. The startup script is designed to fix ownership of the data/ folder.

    NodeNotFoundError: This usually happens if the browser caches an old or corrupted Zarr structure. Perform a Hard Refresh (Ctrl + F5) or open the dashboard in an Incognito window.

    Zarr Versioning: This pipeline strictly enforces Zarr V2 via zarr.DirectoryStore to ensure compatibility with Vitessce’s JavaScript engine.

🛠️ Tech Stack

    LaminDB: Data lineage and metadata management.

    Vitessce: Multi-modal interactive visualization.

    Docker: Reproducible environment.


---



### Next Step:
Once you've saved this file, you are ready to run:
1. `git add .`
2. `git commit -m "Initial commit with English documentation"`
3. `git push`

**Would you like me to generate the `.gitignore` file content for you as well?**