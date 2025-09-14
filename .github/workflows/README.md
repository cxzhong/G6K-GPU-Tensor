# GitHub Actions CI/CD Documentation

This repository includes comprehensive GitHub Actions workflows to ensure build quality and compatibility.

## Workflows

### 1. Build and Test (`build-test.yml`)
**Triggers:** Push to main/dev, Pull Requests, Manual dispatch

**Jobs:**
- **build-gpu**: Tests GPU-enabled builds with CUDA across Python 3.10-3.13
- **build-validation**: Validates GPU package distribution and wheel building
- **code-quality**: Checks code formatting and style with black, isort, flake8
- **dependency-check**: Scans for security vulnerabilities in dependencies

**What it tests:**
- 🚀 GPU-enabled PEP 517/518 compliant build with `pip install -e .`
- 🚀 CUDA Toolkit integration (versions 12.0.0, 12.5.0) using v0.2.27 action
- 🚀 Python version compatibility (3.10-3.13) with GPU support  
- 🚀 GPU-accelerated functionality and imports
- 🚀 SVP challenge execution with CUDA acceleration
- 🚀 Rebuild script functionality with GPU compilation
- 🚀 GPU package distribution quality

### 2. CUDA Build Test (`cuda-test.yml`)
**Triggers:** Push/PR affecting CUDA code, Manual dispatch

**Requirements:** Self-hosted runner with CUDA toolkit

**Jobs:**
- **cuda-build**: Full CUDA compilation and GPU acceleration testing
- **cuda-compatibility**: Static analysis for CUDA compatibility

**What it tests:**
- 🚀 CUDA auto-detection and compilation
- 🚀 GPU-accelerated sieving functionality
- 🚀 Performance benchmarks (manual trigger)
- 🚀 Custom dimension rebuilds
- 🚀 CUDA compatibility checks

## Badge Status

Add this badge to your README.md to show build status:

```markdown
[![Build Status](https://github.com/cxzhong/G6K-GPU-Tensor/actions/workflows/build-test.yml/badge.svg)](https://github.com/cxzhong/G6K-GPU-Tensor/actions/workflows/build-test.yml)
```

## Running Workflows Locally

### GPU-enabled testing (Recommended):
```bash
# Install CUDA Toolkit (12.0.0+ or 12.5.0+)
# Follow NVIDIA CUDA installation guide for your OS

# Install system dependencies
sudo apt-get install build-essential libgmp-dev libmpfr-dev libfplll-dev

# Install parallel-hashmap
git clone https://github.com/greg7mdp/parallel-hashmap.git
cd parallel-hashmap && mkdir build && cd build
cmake .. && make && sudo make install

# Build with GPU acceleration
pip install -e .
python svp_challenge.py 60 --seed 1337
```

### CPU fallback testing:
```bash
# For systems without GPU support
G6K_ENABLE_CUDA=0 pip install -e .
python -c "import g6k; print('✅ CPU fallback success')"
```

## Self-Hosted Runner Setup

For CUDA testing, you'll need a self-hosted GitHub Actions runner:

1. **Set up runner on CUDA-capable machine:**
   ```bash
   # Download and configure GitHub Actions runner
   # Follow: https://github.com/cxzhong/G6K-GPU-Tensor/settings/actions/runners/new
   
   # Install system dependencies
   sudo apt-get install build-essential cmake libgmp-dev libmpfr-dev libfplll-dev
   
   # Install CUDA toolkit (if not already installed)
   # Follow NVIDIA CUDA installation guide for your OS
   ```

2. **Label the runner:** Add `cuda-capable` label in GitHub settings

3. **Update workflow:** Change `runs-on: self-hosted` to `runs-on: [self-hosted, cuda-capable]`

## Troubleshooting

### Common Issues:

1. **Missing system dependencies:**
   ```bash
   sudo apt-get update
   sudo apt-get install build-essential libgmp-dev libmpfr-dev libfplll-dev
   ```

2. **parallel-hashmap not found:**
   - Workflow automatically installs it
   - For local testing, follow installation steps above

3. **CUDA not detected:**
   - Check `nvcc --version`
   - Ensure CUDA toolkit is in PATH
   - Set `G6K_ENABLE_CUDA=0` for CPU-only build

4. **Python version compatibility:**
   - Workflows test Python 3.9-3.13
   - Use `python3.11` or newer for best compatibility

## Manual Testing

### Test complete build process:
```bash
# Clean environment
rm -rf build/ dist/ *.egg-info/ g6k/*.so

# Fresh install
pip install -e . -v

# Run tests
python -c "import g6k; from g6k import Siever; print('✅ Import success')"
python svp_challenge.py 40 --seed 1337
./rebuild.sh --fast
```

### Code quality checks:
```bash
pip install black isort flake8
black --check *.py g6k/
isort --check-only *.py g6k/
flake8 *.py g6k/ --max-line-length=88
```

## Performance Testing

The CUDA workflow includes optional performance benchmarks:
- Triggered manually via "Run workflow" button
- Configurable maximum dimension testing
- Timeout protection (5 minutes)
- Results logged in workflow output

For comprehensive performance testing, use the manual benchmark scripts in `cuda/` directory.