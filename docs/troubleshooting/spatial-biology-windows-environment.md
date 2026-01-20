# Spatial Biology Python Environment - Windows Troubleshooting Guide

**Last Updated:** 2026-01-19
**Environment:** Windows 10/11, Conda/Miniconda, Python 3.10
**Packages:** valis-wsi, pyvips, scanpy, banksy-py, numpy, scipy

## Overview

This guide documents common issues encountered when setting up Python environments for spatial biology analysis on Windows, specifically for workflows involving VALIS image registration, Visium HD analysis, and multi-modal spatial data integration.

---

## Issue 1: fastcluster Build Failure During pip Install

### Symptom

```
ERROR: Failed building wheel for fastcluster
failed-wheel-build-for-install
× Failed to build installable wheels for some pyproject.toml based projects
╰─> fastcluster
```

### Root Cause

The `fastcluster` package requires C compilation, which fails on Windows without proper build tools. The package is a dependency of `valis-wsi`.

### Solution

Install `fastcluster` via conda (pre-compiled binary) before installing `valis-wsi`:

```bash
conda install -c conda-forge fastcluster
pip install valis-wsi  # Now installs without needing to build fastcluster
```

**In environment.yml:**

```yaml
dependencies:
  - fastcluster  # Pre-built from conda-forge

  - pip:
    - valis-wsi>=1.2.0
```

### Alternative

If you must use pip only, install Visual Studio Build Tools:
1. Download from https://visualstudio.microsoft.com/visual-cpp-build-tools/
2. Install with "Desktop development with C++" workload
3. Restart terminal and try again

---

## Issue 2: ModuleNotFoundError: No module named 'numpy.rec'

### Symptom

```python
from valis import registration
# Traceback:
# ModuleNotFoundError: No module named 'numpy.rec'
```

Or when importing scipy:

```python
from scipy import ndimage
# ModuleNotFoundError: No module named 'numpy.rec'
```

### Root Cause

NumPy 1.26+ changed its internal module structure. The `numpy.rec` module can no longer be imported directly as a module (only accessed as an attribute: `numpy.rec`). This breaks compatibility with scipy 1.15.x and valis-wsi when they try to `import numpy.rec`.

### Solution

**Downgrade numpy to 1.24.x:**

```bash
pip install "numpy>=1.23,<1.25" --force-reinstall
```

**In environment.yml:**

```yaml
dependencies:
  - numpy>=1.23,<1.25  # Pinned to 1.24.x for valis compatibility
```

### Verification

```python
import numpy
print(numpy.__version__)  # Should be 1.24.x

import numpy.core.records  # Should work
from valis import registration  # Should work
```

### Why This Works

NumPy 1.24.x maintains backward compatibility with the old module import pattern that scipy and valis expect.

---

## Issue 3: OpenMP Library Conflict

### Symptom

```
OMP: Error #15: Initializing libomp.dll, but found libiomp5md.dll already initialized.
OMP: Hint This means that multiple copies of the OpenMP runtime have been linked into the program.
```

### Root Cause

PyTorch and NumPy/SciPy load different OpenMP runtime libraries (`libiomp5md.dll` vs `libomp.dll`), causing conflicts on Windows.

### Solution 1: Set Environment Variable (Terminal)

```batch
# Windows Command Prompt
set KMP_DUPLICATE_LIB_OK=TRUE

# Windows PowerShell
$env:KMP_DUPLICATE_LIB_OK="TRUE"
```

### Solution 2: Set in Python Script/Notebook

**Add at the very top of your Python script or Jupyter notebook:**

```python
import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
```

### Solution 3: Permanent System Variable

Set as a system environment variable through Windows Settings:
1. Search "Environment Variables" in Windows
2. Add user/system variable: `KMP_DUPLICATE_LIB_OK` = `TRUE`

### Setup Script (setup_env.bat)

```batch
@echo off
set KMP_DUPLICATE_LIB_OK=TRUE
echo [OK] Environment configured
```

Run before starting Jupyter:
```bash
conda activate your_env
setup_env.bat
jupyter lab
```

---

## Issue 4: OSError: cannot load library 'libvips-42.dll'

### Symptom

```python
from valis import registration
# OSError: cannot load library 'libvips-42.dll': error 0x7e
# Additionally, ctypes.util.find_library() did not manage to locate a library called 'libvips-42.dll'
```

**Typically occurs in Jupyter notebooks even when imports work in terminal.**

### Root Cause

1. **libvips not installed** - System library missing
2. **libvips not in PATH** - Windows can't find the DLL
3. **Jupyter kernel doesn't inherit PATH** - Jupyter starts fresh without parent process environment

### Solution 1: Install libvips (if not installed)

**Windows:**
1. Download from https://github.com/libvips/libvips/releases
2. Extract to `C:\vips-dev-8.18\` (or similar)
3. Add to PATH: `C:\vips-dev-8.18\bin`

Verify:
```bash
vips --version
```

### Solution 2: Add libvips to Jupyter Notebook (Recommended)

**Add this cell as the FIRST CELL in your Jupyter notebook:**

```python
# ============================================================
# Environment Setup - Run this cell first!
# ============================================================
import os
import sys

# Fix OpenMP library conflict
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

# Add libvips to PATH and DLL search path
vips_path = r'C:\vips-dev-8.18\bin'  # Update to your installation path
if os.path.exists(vips_path):
    # Add to PATH
    if vips_path not in os.environ['PATH']:
        os.environ['PATH'] = vips_path + os.pathsep + os.environ['PATH']

    # Add to DLL search path (Windows Python 3.8+)
    if sys.platform == 'win32' and hasattr(os, 'add_dll_directory'):
        os.add_dll_directory(vips_path)

    print(f"[OK] libvips path added: {vips_path}")
else:
    print(f"[WARNING] libvips not found at {vips_path}")
    print("  Update vips_path to match your installation")

print("[OK] Environment configured")
```

### Solution 3: Check PATH in Terminal

```bash
# Check if vips is in PATH
where vips

# Check if DLL exists
dir "C:\vips-dev-8.18\bin\libvips-42.dll"
```

### Why Jupyter Needs Special Handling

- Jupyter kernels start as separate processes
- They don't inherit environment variables from the parent shell
- Windows DLL loading is path-dependent
- `os.add_dll_directory()` (Python 3.8+) explicitly tells Python where to find DLLs

---

## Issue 5: banksy-py Dependency Conflicts

### Symptom

```
ERROR: banksy-py 0.0.7 requires numpy==1.22.4, but you have numpy 1.24.4
ERROR: banksy-py 0.0.7 requires pandas==1.5.2, but you have pandas 2.3.3
ERROR: banksy-py 0.0.7 requires scipy==1.10.0, but you have scipy 1.15.3
```

### Root Cause

`banksy-py==0.0.7` has strict version pins for older packages, but it actually works fine with newer versions. The strict pins cause unnecessary downgrades.

### Solution

Install `banksy-py` with `--no-deps` to skip dependency checks:

```bash
pip install banksy-py --no-deps
```

Then ensure compatible versions are installed:

```bash
pip install "numpy>=1.23,<1.25" "pandas>=2.0.0" "scipy>=1.10.0,<2.0"
pip install --upgrade scanpy  # For matplotlib 3.10+ compatibility
```

### Verification

```python
import banksy
import numpy
import pandas
import scipy

print(f"banksy: OK")
print(f"numpy: {numpy.__version__}")  # 1.24.4
print(f"pandas: {pandas.__version__}")  # 2.3.3
print(f"scipy: {scipy.__version__}")  # 1.15.3
```

---

## Complete Working Configuration

### Package Versions

```
Python: 3.10.19
numpy: 1.24.4 (pinned for valis compatibility)
scipy: 1.15.3
pandas: 2.3.3
matplotlib: 3.10.8
scikit-learn: 1.5.2-1.7.2
scikit-image: 0.25.2
pyvips: 3.1.1
valis-wsi: 1.2.0
scanpy: 1.11.5
banksy-py: 0.0.7 (installed with --no-deps)
fastcluster: 1.2.6 (from conda-forge)
libvips: 8.18.0 (system library)
```

### environment.yml Example

```yaml
name: spatial_bio
channels:
  - conda-forge
  - bioconda
  - defaults

dependencies:
  - python=3.10

  # Core scientific computing
  - numpy>=1.23,<1.25  # Pinned for valis compatibility
  - pandas>=2.0.0
  - scipy>=1.10.0,<2.0.0

  # Pre-built packages to avoid compilation
  - fastcluster  # Required by valis-wsi

  # Single-cell and spatial transcriptomics
  - scanpy>=1.10.0
  - anndata>=0.8

  # Machine learning
  - scikit-learn>=1.2.0,<2.0
  - scikit-image>=0.24.0,<1.0

  # Deep learning (required by VALIS)
  - pytorch>=2.0.0
  - torchvision>=0.15.0

  # Jupyter
  - jupyterlab>=4.0.0

  - pip:
    - valis-wsi>=1.2.0
    - pyvips>=2.2.1
    - banksy-py --no-deps  # Note: --no-deps not supported in YAML
```

**Note:** Install banksy-py separately after environment creation:
```bash
conda activate spatial_bio
pip install banksy-py --no-deps
```

---

## Installation Sequence (Recommended)

### 1. Install System Dependencies

```bash
# Install libvips for Windows
# Download from: https://github.com/libvips/libvips/releases
# Extract to: C:\vips-dev-8.18\
# Add to PATH: C:\vips-dev-8.18\bin
```

### 2. Create Conda Environment

```bash
conda env create -f environment.yml
conda activate spatial_bio
```

### 3. Install pip Packages with Correct Order

```bash
# Install fastcluster first (if not from conda)
conda install -c conda-forge fastcluster

# Install numpy at correct version
pip install "numpy>=1.23,<1.25" --force-reinstall

# Install other dependencies
pip install "scipy>=1.10.0,<2.0" "pandas>=2.0.0" "matplotlib>=3.6.3"

# Install valis and pyvips
pip install pyvips valis-wsi

# Install banksy without dependencies
pip install banksy-py --no-deps

# Upgrade scanpy for matplotlib compatibility
pip install --upgrade scanpy
```

### 4. Verify Installation

```python
import os
import sys

# Configure environment
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
vips_path = r'C:\vips-dev-8.18\bin'
if hasattr(os, 'add_dll_directory'):
    os.add_dll_directory(vips_path)

# Test imports
import numpy
import scipy
import pandas
import pyvips
from valis import registration
import scanpy
import banksy

print("[OK] All packages imported successfully")
print(f"numpy: {numpy.__version__}")
print(f"valis: working")
```

---

## Jupyter Notebook Template

**Save this as a template for all spatial biology notebooks:**

```python
# ============================================================
# CELL 1: Environment Setup (RUN FIRST!)
# ============================================================
import os
import sys

# Fix OpenMP library conflict (PyTorch + NumPy)
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

# Add libvips to DLL search path (Windows)
vips_path = r'C:\vips-dev-8.18\bin'
if os.path.exists(vips_path):
    if vips_path not in os.environ['PATH']:
        os.environ['PATH'] = vips_path + os.pathsep + os.environ['PATH']

    if sys.platform == 'win32' and hasattr(os, 'add_dll_directory'):
        os.add_dll_directory(vips_path)

    print(f"[OK] Environment configured: {vips_path}")
else:
    print(f"[WARNING] libvips not found at {vips_path}")

# ============================================================
# CELL 2: Imports
# ============================================================
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import tifffile as tiff
from valis import registration
import scanpy as sc

# ============================================================
# CELL 3+: Your Analysis
# ============================================================
# ... your code here ...
```

---

## Troubleshooting Checklist

When encountering import errors, check in this order:

- [ ] Is the conda environment activated? (`conda activate spatial_bio`)
- [ ] Is libvips installed? (`vips --version`)
- [ ] Is numpy version 1.24.x? (`python -c "import numpy; print(numpy.__version__)"`)
- [ ] Is OpenMP variable set? (`echo %KMP_DUPLICATE_LIB_OK%`)
- [ ] For Jupyter: Did you add the setup code to the first cell?
- [ ] For Jupyter: Did you restart the kernel after adding setup code?
- [ ] Is fastcluster from conda? (`conda list fastcluster`)
- [ ] Is banksy-py installed with `--no-deps`? (`pip show banksy-py`)

---

## Platform-Specific Notes

### Windows Considerations

1. **DLL Loading:** Windows requires explicit DLL directory specification in Python 3.8+
2. **PATH Issues:** Jupyter doesn't inherit PATH from terminal
3. **Build Tools:** C/C++ compilation requires Visual Studio Build Tools
4. **Conda vs Pip:** Prefer conda for packages requiring compilation (fastcluster, numpy, scipy)

### Why These Issues Don't Occur on Linux/macOS

- System library paths are better integrated (`LD_LIBRARY_PATH`, `DYLD_LIBRARY_PATH`)
- Compilation toolchains (gcc, clang) are typically pre-installed
- OpenMP libraries are more consistently managed
- Jupyter better inherits environment variables

---

## References

- **VALIS Documentation:** https://valis.readthedocs.io/
- **libvips Releases:** https://github.com/libvips/libvips/releases
- **NumPy 1.26 Release Notes:** https://numpy.org/doc/stable/release/1.26.0-notes.html
- **BANKSY Documentation:** https://github.com/prabhakarlab/Banksy_py
- **Scanpy Documentation:** https://scanpy.readthedocs.io/

---

## Related Issues

- NumPy issue on module restructuring: https://github.com/numpy/numpy/issues/24248
- SciPy compatibility: https://github.com/scipy/scipy/issues/18825
- VALIS Windows installation: https://github.com/MathOnco/valis/issues

---

## Version History

- **2026-01-19:** Initial documentation based on maitra_sow124 environment setup
  - Documented fastcluster, numpy.rec, OpenMP, libvips DLL, and banksy-py issues
  - Tested on Windows 10, Python 3.10.19, valis-wsi 1.2.0

---

## Contributing

If you encounter additional issues or find solutions not documented here, please:
1. Update this document
2. Add your findings with dates and package versions
3. Include minimal reproducible examples
4. Document the root cause when known

---

**Maintained by:** Astraea Bio Ops Team
**Contact:** [Add contact information]
