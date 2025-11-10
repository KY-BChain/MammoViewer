#!/usr/bin/env python3
"""
MammoViewer Installation Test Script

Tests the installation to ensure all dependencies are correctly installed
and the system is ready to run MammoViewer.
"""

import sys
import os
from pathlib import Path


class Colors:
    """ANSI color codes for terminal output."""
    GREEN = '\033[0;32m'
    RED = '\033[0;31m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color

    @staticmethod
    def is_windows():
        return sys.platform.startswith('win')

    @classmethod
    def disable_on_windows(cls):
        """Disable colors on Windows (unless ANSI support is enabled)."""
        if cls.is_windows():
            cls.GREEN = cls.RED = cls.YELLOW = cls.BLUE = cls.NC = ''


# Disable colors on Windows by default
if sys.platform.startswith('win'):
    Colors.disable_on_windows()


def print_success(message):
    """Print success message."""
    print(f"{Colors.GREEN}✓{Colors.NC} {message}")


def print_error(message):
    """Print error message."""
    print(f"{Colors.RED}✗{Colors.NC} {message}")


def print_warning(message):
    """Print warning message."""
    print(f"{Colors.YELLOW}⚠{Colors.NC} {message}")


def print_info(message):
    """Print info message."""
    print(f"{Colors.BLUE}ℹ{Colors.NC} {message}")


def test_python_version():
    """Test Python version is 3.8 or higher."""
    print("\n1. Testing Python version...")

    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"

    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print_error(f"Python {version_str} is too old")
        print_info("Python 3.8 or higher is required")
        return False

    print_success(f"Python {version_str}")
    return True


def test_required_packages():
    """Test that all required packages are installed."""
    print("\n2. Testing required packages...")

    required_packages = [
        'flask',
        'flask_cors',
        'pydicom',
        'SimpleITK',
        'numpy',
        'vtk',
        'pyvista',
        'PIL',
        'cv2',
        'magic',
        'dotenv',
        'werkzeug',
        'sqlalchemy',
        'celery',
        'redis',
        'tqdm',
        'loguru',
        'uuid',
        'jsonschema',
        'requests',
        'pytest'
    ]

    all_installed = True
    missing_packages = []

    for package in required_packages:
        try:
            if package == 'flask_cors':
                __import__('flask_cors')
            elif package == 'PIL':
                __import__('PIL')
            elif package == 'cv2':
                __import__('cv2')
            elif package == 'magic':
                __import__('magic')
            elif package == 'dotenv':
                __import__('dotenv')
            else:
                __import__(package)

            # Don't print success for each package to keep output clean
        except ImportError:
            missing_packages.append(package)
            all_installed = False

    if all_installed:
        print_success(f"All {len(required_packages)} required packages are installed")
        return True
    else:
        print_error(f"Missing packages: {', '.join(missing_packages)}")
        print_info("Run: pip install -r backend/requirements.txt")
        return False


def test_directories():
    """Test that all required directories exist."""
    print("\n3. Testing project directories...")

    required_dirs = [
        'backend',
        'frontend',
        'uploads',
        'outputs',
        'temp',
        'logs',
        'slicer_scripts'
    ]

    all_exist = True
    missing_dirs = []

    for directory in required_dirs:
        path = Path(directory)
        if not path.exists():
            missing_dirs.append(directory)
            all_exist = False
        elif not path.is_dir():
            print_error(f"{directory} exists but is not a directory")
            all_exist = False

    if all_exist:
        print_success(f"All {len(required_dirs)} required directories exist")
        return True
    else:
        print_error(f"Missing directories: {', '.join(missing_dirs)}")
        print_info("Create them with: mkdir -p " + ' '.join(missing_dirs))
        return False


def test_directory_permissions():
    """Test write permissions on critical directories."""
    print("\n4. Testing directory permissions...")

    write_dirs = ['uploads', 'outputs', 'temp', 'logs', 'slicer_scripts']

    all_writable = True

    for directory in write_dirs:
        path = Path(directory)
        if path.exists():
            if os.access(path, os.W_OK):
                # Success - don't print for each
                pass
            else:
                print_error(f"{directory} is not writable")
                all_writable = False

    if all_writable:
        print_success("All directories are writable")
        return True
    else:
        print_info("Fix permissions with: chmod -R 755 <directory>")
        return False


def test_config_file():
    """Test configuration file."""
    print("\n5. Testing configuration...")

    env_file = Path('.env')

    if not env_file.exists():
        print_warning(".env file does not exist")
        print_info("Copy .env.example to .env and configure it")
        return False

    # Try to import config module
    try:
        sys.path.insert(0, str(Path.cwd()))
        from backend import config

        print_success("Configuration module loaded successfully")

        # Test Slicer path
        slicer_path = Path(config.SLICER_PATH)
        if slicer_path.exists():
            print_success(f"3D Slicer found at: {config.SLICER_PATH}")
        else:
            print_warning(f"3D Slicer not found at: {config.SLICER_PATH}")
            print_info("Install 3D Slicer and update SLICER_PATH in .env")

        return True

    except Exception as e:
        print_error(f"Failed to load configuration: {e}")
        return False


def test_backend_modules():
    """Test that backend modules can be imported."""
    print("\n6. Testing backend modules...")

    modules = [
        'backend.config',
        'backend.dicom_processor',
        'backend.slicer_converter',
        'backend.app'
    ]

    all_imported = True

    for module in modules:
        try:
            __import__(module)
            # Success - don't print for each
        except Exception as e:
            print_error(f"Failed to import {module}: {e}")
            all_imported = False

    if all_imported:
        print_success(f"All {len(modules)} backend modules imported successfully")
        return True
    else:
        return False


def test_frontend_files():
    """Test that frontend files exist."""
    print("\n7. Testing frontend files...")

    frontend_files = [
        'frontend/index.html',
        'frontend/styles.css',
        'frontend/app.js'
    ]

    all_exist = True

    for file_path in frontend_files:
        path = Path(file_path)
        if not path.exists():
            print_error(f"{file_path} does not exist")
            all_exist = False

    if all_exist:
        print_success(f"All {len(frontend_files)} frontend files exist")
        return True
    else:
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("  MammoViewer Installation Test")
    print("=" * 60)

    tests = [
        ("Python version", test_python_version),
        ("Required packages", test_required_packages),
        ("Project directories", test_directories),
        ("Directory permissions", test_directory_permissions),
        ("Configuration", test_config_file),
        ("Backend modules", test_backend_modules),
        ("Frontend files", test_frontend_files)
    ]

    results = []

    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print_error(f"Test '{test_name}' failed with exception: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 60)
    print("  Test Summary")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = f"{Colors.GREEN}PASS{Colors.NC}" if result else f"{Colors.RED}FAIL{Colors.NC}"
        print(f"{status}  {test_name}")

    print("=" * 60)

    if passed == total:
        print_success(f"All {total} tests passed!")
        print("\nYou're ready to run MammoViewer:")
        print(f"{Colors.GREEN}  python backend/app.py{Colors.NC}")
        return 0
    else:
        print_warning(f"{passed}/{total} tests passed, {total - passed} failed")
        print("\nPlease fix the issues above before running MammoViewer")
        return 1


if __name__ == '__main__':
    sys.exit(main())
