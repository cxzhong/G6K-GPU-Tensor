#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext as _build_ext
import subprocess
import os
import sys
import glob
import shutil
from pathlib import Path

# Install dependencies first if needed
def install_fpylll():
    """Install fpylll if not already available."""
    try:
        import fpylll
        print("FPyLLL already installed")
        return True
    except ImportError:
        pass
    
    print("Installing FPyLLL...")
    try:
        # Try different approaches to install fpylll
        pip_commands = [
            [sys.executable, '-m', 'pip', 'install', 'fpylll'],
            ['pip3', 'install', 'fpylll'],
            ['pip', 'install', 'fpylll']
        ]
        
        for cmd in pip_commands:
            try:
                subprocess.check_call(cmd)
                print("FPyLLL installed successfully")
                return True
            except (subprocess.CalledProcessError, FileNotFoundError):
                continue
        
        print("Could not install FPyLLL automatically.")
        print("Please install it manually using: pip install fpylll")
        return False
        
    except Exception as e:
        print(f"Error during FPyLLL installation: {e}")
        print("You may need to install it manually using: pip install fpylll")
        return False

# FPyLLL will be installed during build process via CustomBuildExt

# Now import required modules
try:
    from Cython.Build import cythonize
    import numpy
except ImportError as e:
    print(f"Missing required build dependency: {e}")
    sys.exit(1)

class CustomBuildExt(_build_ext):
    """Custom build_ext command to handle dependencies."""
    
    def run(self):
        # Install system dependencies first
        self.install_system_deps()
        
        # Install fpylll if not available  
        install_fpylll()
        
        # Install FPLLL if needed
        self.install_fplll()
        
        # Run the build
        _build_ext.run(self)
        
    def install_system_deps(self):
        """Install required system dependencies."""
        try:
            # Check if parallel-hashmap headers are available
            if not os.path.exists('/usr/include/parallel_hashmap/phmap.h'):
                print("Installing parallel-hashmap system dependency...")
                subprocess.check_call(['sudo', 'apt', 'update'], stdout=subprocess.DEVNULL)
                subprocess.check_call(['sudo', 'apt', 'install', '-y', 'libparallel-hashmap-dev'], 
                                    stdout=subprocess.DEVNULL)
                print("parallel-hashmap installed successfully")
        except Exception as e:
            print(f"Warning: Could not install system dependencies: {e}")
            print("Please install manually: sudo apt install libparallel-hashmap-dev")
            
    def install_fplll(self):
        """Install FPLLL if not available."""
        try:
            # Check if FPLLL is available
            result = subprocess.run(['pkg-config', '--exists', 'fplll'], 
                                  capture_output=True)
            if result.returncode != 0:
                print("Installing FPLLL...")
                # Run our install script
                subprocess.check_call(['./install-deps.sh'], 
                                    cwd=os.path.dirname(os.path.abspath(__file__)))
                print("FPLLL installed successfully")
        except Exception as e:
            print(f"Warning: Could not install FPLLL: {e}")
            print("FPLLL may need to be installed manually")

def install_system_dependencies():
    """Install FPLLL and FPyLLL if not available."""
    cwd = os.getcwd()
    
    try:
        print("Checking for FPLLL system library...")
        
        # Check if fplll is available via pkg-config
        fplll_found = False
        try:
            result = subprocess.run(["pkg-config", "--exists", "fplll"], 
                                  capture_output=True, check=False)
            if result.returncode == 0:
                print("FPLLL found via pkg-config")
                fplll_found = True
        except FileNotFoundError:
            pass
        
        # Check if we're in a virtual environment with fplll installed
        if not fplll_found and os.environ.get('VIRTUAL_ENV'):
            fplll_lib = Path(os.environ['VIRTUAL_ENV']) / "lib" / "libfplll.so"
            if fplll_lib.exists():
                print(f"FPLLL found in virtual environment: {fplll_lib}")
                fplll_found = True
        
        # Try to find system fplll
        if not fplll_found:
            for lib_path in ["/usr/lib", "/usr/local/lib", "/usr/lib/x86_64-linux-gnu"]:
                if any(Path(lib_path).glob("libfplll*")):
                    print(f"FPLLL found in system: {lib_path}")
                    fplll_found = True
                    break
        
        # Install FPLLL if not found
        if not fplll_found:
            print("FPLLL not found. Installing from source...")
            
            # Clone and build FPLLL if needed
            fplll_dir = Path("g6k-fplll")
            if not fplll_dir.exists():
                print("Cloning FPLLL...")
                subprocess.check_call([
                    "git", "clone", 
                    "https://github.com/fplll/fplll", 
                    str(fplll_dir)
                ])
            
            # Build and install FPLLL
            os.chdir(fplll_dir)
            try:
                if not Path("configure").exists():
                    subprocess.check_call("./autogen.sh", shell=True)
                
                # Configure with appropriate prefix
                prefix = os.environ.get('VIRTUAL_ENV', '/usr/local')
                subprocess.check_call(f"./configure --prefix={prefix}", shell=True)
                
                # Build and install
                subprocess.check_call("make clean", shell=True)
                subprocess.check_call("make -j$(nproc)", shell=True) 
                subprocess.check_call("make install", shell=True)
                print("FPLLL installed successfully")
                
            except subprocess.CalledProcessError as e:
                print(f"Warning: FPLLL installation failed: {e}")
                print("You may need to install FPLLL system dependencies first.")
                print("Try: sudo apt-get install libgmp-dev libmpfr-dev")
            finally:
                os.chdir(cwd)
        
        # Now install FPyLLL
        print("Checking for FPyLLL...")
        try:
            import fpylll
            print("FPyLLL already available")
        except ImportError:
            print("Installing FPyLLL...")
            
            # Clone FPyLLL if needed
            fpylll_dir = Path("g6k-fpylll")
            if not fpylll_dir.exists():
                print("Cloning FPyLLL...")
                subprocess.check_call([
                    "git", "clone",
                    "https://github.com/fplll/fpylll",
                    str(fpylll_dir)
                ])
            
            # Install FPyLLL using pip
            try:
                os.chdir(fpylll_dir)
                subprocess.check_call([sys.executable, "-m", "pip", "install", "."])
                print("FPyLLL installed successfully")
            except subprocess.CalledProcessError as e:
                print(f"Warning: FPyLLL installation failed: {e}")
            finally:
                os.chdir(cwd)
                
    except Exception as e:
        print(f"Error during dependency installation: {e}")
    finally:
        # Always return to original directory
        os.chdir(cwd)

def ensure_parallel_hashmap():
    """Ensure parallel-hashmap dependency is available."""
    hashmap_dir = Path("parallel-hashmap")
    if not hashmap_dir.exists():
        print("Cloning parallel-hashmap dependency...")
        subprocess.check_call([
            "git", "clone", 
            "https://github.com/cr-marcstevens/parallel-hashmap",
            str(hashmap_dir)
        ])

def build_kernel_library():
    """Build the kernel library using make."""
    print("Building kernel library...")
    
    # Check if Makefile.local exists, create it if not
    makefile_local = Path("Makefile.local")
    if not makefile_local.exists():
        print("Creating Makefile.local...")
        subprocess.check_call("./rebuild.sh --onlyconf", shell=True)
    
    # Build the kernel library
    try:
        subprocess.check_call("make -C kernel", shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to build kernel library: {e}")
        print("You may need to run './rebuild.sh' to configure the build properly.")
        sys.exit(1)

def read_from_makefile(field):
    """Read build variables from kernel/Makefile."""
    try:
        makefile_defs = subprocess.getoutput("make -C kernel printvariables | grep '='").splitlines()
        data = [line for line in makefile_defs if line.startswith(field)]
        if not data:
            print(f"Warning: Could not find {field} in Makefile variables")
            return []
        
        data = data[0]
        data = '='.join(data.split('=')[1:])
        data = data.strip()
        data = [arg for arg in data.split(' ') if arg.strip()]
        return data
    except Exception as e:
        print(f"Warning: Failed to read {field} from Makefile: {e}")
        return []

def get_extension_modules():
    """Configure and return Cython extension modules."""
    
    # Install system dependencies first
    install_system_dependencies()
    
    # Ensure dependencies are available
    ensure_parallel_hashmap() 
    build_kernel_library()
    
    # Read build configuration from Makefile
    extra_compile_args = read_from_makefile("CXXFLAGS")
    extra_link_args = read_from_makefile("LDFLAGS") + read_from_makefile("LIBADD")
    
    # Fallback compile args if Makefile reading fails
    if not extra_compile_args:
        extra_compile_args = [
            "-fPIC", "-Ofast", "-march=native", "-ftree-vectorize", 
            "-funroll-loops", "-std=c++17", "-pthread", "-Wall", "-Wextra"
        ]
    
    if not extra_link_args:
        extra_link_args = ["-shared", "-pthread", "-lpthread"]
    
    # Library path for libG6K.so
    kernel_lib_path = os.path.abspath("kernel")
    extra_link_args.extend([f"-L{kernel_lib_path}", f"-Wl,-rpath={kernel_lib_path}"])
    
    kwds = {
        "language": "c++",
        "extra_compile_args": extra_compile_args,
        "extra_link_args": extra_link_args, 
        "libraries": ["gmp", "pthread", "G6K"],
        "library_dirs": [kernel_lib_path],
        "include_dirs": [numpy.get_include(), "parallel-hashmap", "kernel"],
        "runtime_library_dirs": [kernel_lib_path]
    }

    extensions = [
        Extension("g6k.siever", ["g6k/siever.pyx"], **kwds),
        Extension("g6k.siever_params", ["g6k/siever_params.pyx"], **kwds)
    ]

    return cythonize(
        extensions, 
        compiler_directives={
            'binding': True,
            'embedsignature': True,
            'language_level': 3
        }
    )

def load_rebuild_config():
    """Load configuration from rebuild.sh if available."""
    config = {
        'MAX_SIEVING_DIM': 128,
        'GPUVECNUM': 65536,
        'EXTRAFLAGS': '',
        'HAVE_CUDA': None,  # Auto-detect if not specified
        'CUDA_PATH': '/usr/local/cuda'
    }
    
    try:
        import compile_config
        rebuild_config = compile_config.REBUILD_CONFIG
        config.update(rebuild_config)
        print(f"Using rebuild.sh configuration: MAX_SIEVING_DIM={config['MAX_SIEVING_DIM']}")
    except ImportError:
        print("No rebuild.sh configuration found, using defaults")
    
    return config

def compile_cuda_objects(config=None):
    """Compile CUDA objects if CUDA is available."""
    if config is None:
        config = load_rebuild_config()
        
    cuda_obj_path = 'cuda/GPUStreamGeneral.o'
    cuda_src_path = 'cuda/GPUStreamGeneral.cu'
    
    if not os.path.exists(cuda_src_path):
        return None
        
    # Check if we need to recompile
    if not os.path.exists(cuda_obj_path) or \
       os.path.getmtime(cuda_src_path) > os.path.getmtime(cuda_obj_path):
        
        print("Compiling CUDA objects...")
        
        max_sieving_dim = config.get('MAX_SIEVING_DIM', 128)
        gpuvecnum = config.get('GPUVECNUM', 65536)
        cuda_path = config.get('CUDA_PATH', '/usr/local/cuda')
        
        nvcc_cmd = [
            f'{cuda_path}/bin/nvcc',
            '-ccbin', 'g++',
            '-Xcompiler', '-fPIC',
            '-Xcompiler', '-Ofast',
            '-Xcompiler', '-march=native',
            '-Xcompiler', '-mno-amx-tile',
            '-Xcompiler', '-mno-amx-int8', 
            '-Xcompiler', '-mno-amx-bf16',
            '-Xcompiler', '-pthread',
            '-Xcompiler', '-Wall',
            '-Xcompiler', '-Wextra',
            '-Xcompiler', f'-DMAX_SIEVING_DIM={max_sieving_dim}',
            '-Xcompiler', f'-DGPUVECNUM={gpuvecnum}',
            '-Xcompiler', '-DHAVE_CUDA',
            '-std=c++17',
            '-O3',
            '--use_fast_math',
            '-Xptxas=-O3,-dlcm=ca',
            '-diag-suppress', '191',
            '-gencode', 'arch=compute_89,code=sm_89',
            '-gencode', 'arch=compute_89,code=compute_89',
            '-lineinfo',
            f'-I{cuda_path}/include',
            '-I../parallel-hashmap',
            '-c', cuda_src_path,
            '-o', cuda_obj_path
        ]
        
        try:
            subprocess.run(nvcc_cmd, check=True, cwd='.')
            print(f"Successfully compiled {cuda_obj_path}")
            return cuda_obj_path
        except subprocess.CalledProcessError as e:
            print(f"Failed to compile CUDA objects: {e}")
            return None
    else:
        print(f"CUDA object {cuda_obj_path} is up to date")
        return cuda_obj_path

def get_ext_modules():
    """Get extension modules after setting up dependencies."""
    ext_modules = []

    try:
        # Load configuration from rebuild.sh if available
        config = load_rebuild_config()
        
        # Check if we should build CUDA extensions
        if config.get('HAVE_CUDA') == 1:
            build_cuda = True
        elif config.get('HAVE_CUDA') == 0:
            build_cuda = False
        else:
            # Auto-detect CUDA
            build_cuda = os.path.exists('/usr/local/cuda') and shutil.which('nvcc')
        
        cuda_obj_path = None
        
        if build_cuda:
            # Compile CUDA objects with configuration
            cuda_obj_path = compile_cuda_objects(config)
            if not cuda_obj_path:
                print("Failed to compile CUDA objects, falling back to CPU-only")
                build_cuda = False
        
        print(f"Building G6K GPU Tensor extensions (CUDA: {'enabled' if build_cuda else 'disabled'})")
        
        # Add cysignals include directory
        cysignals_include = None
        try:
            import cysignals
            cysignals_include = os.path.dirname(cysignals.__file__)
        except ImportError:
            pass

        include_dirs = [
            'kernel',
            numpy.get_include(),
            '/usr/include'
        ]
        
        if cysignals_include:
            include_dirs.append(cysignals_include)
            
        if build_cuda:
            include_dirs.extend([
                'cuda',
                '/usr/local/cuda/include'
            ])

        # Build main siever extension
        sources = ['g6k/siever.pyx']
        
        # Add all kernel files including GPU sieve
        kernel_sources = [
            'kernel/bgj1_sieve.cpp',
            'kernel/control.cpp',
            'kernel/cpuperf.cpp', 
            'kernel/gpu_sieve.cpp',
            'kernel/params.cpp',
            'kernel/sieving.cpp',
            'kernel/triple_sieve.cpp',
            'kernel/triple_sieve_mt.cpp'
        ]
        sources += kernel_sources
        
        # Add CUDA object as extra link arg if available
        extra_link_args = ['-lpthread', '-lm']
        if build_cuda and cuda_obj_path and os.path.exists(cuda_obj_path):
            extra_link_args.append(cuda_obj_path)
            # Add CUDA-specific linker flags
            extra_link_args.extend([
                '-L/usr/local/cuda/lib64',
                '-L/usr/lib/wsl/lib', 
                '-L/usr/local/cuda/targets/x86_64-linux/lib',
                '-L/usr/local/cuda/lib64/stubs',
                '-Wl,-rpath,/usr/local/cuda/lib64',
                '-Wl,-rpath,/usr/lib/wsl/lib',
                '-Wl,-rpath,/usr/local/cuda/targets/x86_64-linux/lib',
                '-lcudart',
                '-lcuda',
                '-lcublas',
                '-lcurand'
            ])
        
        # Libraries and library directories
        libraries = ['pthread', 'm']
        library_dirs = ['/usr/lib/x86_64-linux-gnu']
        
        if build_cuda:
            libraries.extend(['cuda', 'cudart', 'cublas', 'curand'])
            library_dirs.extend([
                '/usr/local/cuda/lib64',
                '/usr/lib/wsl/lib',
                '/usr/local/cuda/targets/x86_64-linux/lib',
                '/usr/local/cuda/lib64/stubs'
            ])

        # Define macros from configuration
        define_macros = []
        max_sieving_dim = config.get('MAX_SIEVING_DIM', 128)
        gpuvecnum = config.get('GPUVECNUM', 65536)
        
        define_macros.extend([
            ('MAX_SIEVING_DIM', str(max_sieving_dim)),
            ('GPUVECNUM', str(gpuvecnum))
        ])
        
        if build_cuda:
            define_macros.extend([
                ('G6K_CUDA', '1'),
                ('HAVE_CUDA', '1')
            ])
            
        # Add extra flags from rebuild.sh
        extra_flags = config.get('EXTRAFLAGS', '')
        if extra_flags:
            for flag in extra_flags.split():
                if flag.startswith('-D'):
                    flag_def = flag[2:]  # Remove -D prefix
                    if '=' in flag_def:
                        name, value = flag_def.split('=', 1)
                        define_macros.append((name, value))
                    else:
                        define_macros.append((flag_def, '1'))

        # Add runtime library paths for CUDA
        runtime_library_dirs = []
        if build_cuda:
            runtime_library_dirs.extend([
                '/usr/local/cuda/lib64',
                '/usr/lib/wsl/lib',
                '/usr/local/cuda/targets/x86_64-linux/lib'
            ])

        ext_modules.append(Extension(
            'g6k.siever',
            sources=sources,
            libraries=libraries,
            library_dirs=library_dirs,
            runtime_library_dirs=runtime_library_dirs,
            language='c++',
            include_dirs=include_dirs,
            extra_compile_args=['-std=c++17', '-O3', '-march=native'],
            extra_link_args=extra_link_args,
            define_macros=define_macros
        ))
        
        # Also build siever_params  
        ext_modules.append(Extension(
            'g6k.siever_params',
            sources=['g6k/siever_params.pyx'],
            include_dirs=include_dirs,
            language='c++',
            extra_compile_args=['-std=c++17', '-O3']
        ))
        
    except Exception as e:
        print(f"Warning: Could not configure C++ extensions: {e}")
        print("Building without native acceleration...")
        
        # Fallback - no extensions
        pass

    return ext_modules

if __name__ == "__main__":
    setup(
        use_scm_version=True,
        cmdclass={'build_ext': CustomBuildExt},
        ext_modules=get_ext_modules(),
        zip_safe=False
    )
