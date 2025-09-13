# Modern G6K Installation Guide

This guide explains how to install G6K GPU Tensor using modern Python packaging standards (PEP 517/518) with `pip install -e .` instead of the legacy `bootstrap.sh` script.

## Quick Start

### Option 1: Automated Installation (Recommended)
```bash
# Create and activate virtual environment
python3 -m venv g6k-env
source g6k-env/bin/activate

# Install system dependencies (fplll, fpylll)
./install-deps.sh

# Install G6K in development mode
pip install -e .

# Test installation
python -c "import g6k; print('G6K imported successfully!')"
```

### Option 2: Manual Installation
```bash
# Create and activate virtual environment  
python3 -m venv g6k-env
source g6k-env/bin/activate

# Upgrade pip and install build tools
pip install --upgrade pip setuptools wheel

# Install build dependencies
pip install Cython cysignals numpy

# Install system dependencies manually (see below)
# ... install fplll and fpylll ...

# Install G6K
pip install -e .
```

## System Dependencies

G6K requires the following system-level dependencies that must be installed before running `pip install -e .`:

### 1. FPLLL (Floating Point LLL)
FPLLL is a C++ library that requires traditional compilation:
```bash
git clone https://github.com/fplll/fplll g6k-fplll
cd g6k-fplll
./autogen.sh
./configure --prefix="$VIRTUAL_ENV"  # or --prefix="$HOME/.local"
make -j$(nproc)
make install
cd ..
```

### 2. FPyLLL (Python wrapper for FPLLL)
FPyLLL supports modern PEP 517 packaging:
```bash
git clone https://github.com/fplll/fpylll g6k-fpylll
cd g6k-fpylll
pip install .
cd ..
```

### 3. CUDA Toolkit (Optional, for GPU acceleration)
Install CUDA toolkit from NVIDIA if you want GPU features:
- Ubuntu: `sudo apt install nvidia-cuda-toolkit`
- Or download from: https://developer.nvidia.com/cuda-downloads

## Development Installation

For development, install with optional dependencies:
```bash
pip install -e .[dev]
```

This includes additional tools like flake8, pytest, and ipython.

## Build Configuration

The new system automatically:
1. Clones `parallel-hashmap` dependency if missing
2. Creates `Makefile.local` configuration if needed
3. Builds the kernel library (`libG6K.so`)
4. Compiles Cython extensions with proper flags
5. Sets up runtime library paths

### Custom Build Options

You can still use the `rebuild.sh` script for advanced build configuration:
```bash
# Fast optimized build
./rebuild.sh -f -y

# With custom max sieving dimension
./rebuild.sh -m 256

# With specific job count
./rebuild.sh -j 8

# Enable debugging
./rebuild.sh -g
```

After running `rebuild.sh`, you can install with:
```bash
pip install -e . --force-reinstall
```

## Environment Variables

For optimal performance, set these environment variables (automatically set by `install-deps.sh`):
```bash
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export CFLAGS="$CFLAGS -O3 -march=native -Wp,-U_FORTIFY_SOURCE"
export CXXFLAGS="$CXXFLAGS -O3 -march=native -Wp,-U_FORTIFY_SOURCE"
```

## Comparison with Legacy Bootstrap

| Aspect | Legacy (`bootstrap.sh`) | Modern (`pip install -e .`) |
|--------|------------------------|----------------------------|
| Standard | Custom script | PEP 517/518 compliant |
| Dependencies | Bundled in script | Declared in `pyproject.toml` |
| Virtual env | Creates `g6k-gpu-env` | Uses any virtual environment |
| Installation | `python setup.py install` | `pip install -e .` |
| Editable install | Manual rebuild needed | Automatic with `-e` flag |
| IDE integration | Limited | Full support |
| Package management | Manual | Standard pip/conda |

## Troubleshooting

### Build Errors
If you encounter build errors:
1. Ensure all system dependencies are installed
2. Check that CUDA toolkit is properly installed (if using GPU features)
3. Try running `./rebuild.sh --onlyconf` to regenerate configuration
4. Clean and rebuild: `make clean && pip install -e . --force-reinstall`

### Import Errors
If G6K fails to import:
1. Check that `libG6K.so` was built successfully in the `kernel/` directory
2. Verify virtual environment is activated
3. Check library paths are set correctly

### CUDA Issues
If CUDA features are not working:
1. Verify CUDA toolkit installation: `nvcc --version`
2. Check that GPU compute capability is supported (SM 80+)
3. Ensure CUDA libraries are in `LD_LIBRARY_PATH`

## Migration from Bootstrap Script

To migrate an existing installation:
```bash
# Backup existing environment
mv g6k-gpu-env g6k-gpu-env.old

# Create new environment and install
python3 -m venv g6k-env
source g6k-env/bin/activate
./install-deps.sh
pip install -e .

# Test everything works
python -c "import g6k; print('Migration successful!')"

# Remove old environment when satisfied
rm -rf g6k-gpu-env.old
```

This modern approach provides better integration with Python tooling while maintaining all the functionality of the original bootstrap script.