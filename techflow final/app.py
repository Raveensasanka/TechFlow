#!/usr/bin/env python3
"""
TechFlow Issue Tracking System - Startup Script
Run this script to start the application with proper configuration
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'flask',
        'pandas',
        'openpyxl',
        'werkzeug'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} is installed")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} is missing")
    
    if missing_packages:
        print(f"\n📦 Installing missing packages: {', '.join(missing_packages)}")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
            print("✅ All dependencies installed successfully")
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies")
            print("Please run: pip install -r requirements.txt")
            return False
    
    return True

def create_directories():
    """Create necessary directories"""
    directories = [
        'static/uploads',
        'static',
        'templates'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Directory created/verified: {directory}")

def check_files():
    """Check if required files exist"""
    required_files = [
        'app.py',
        'requirements.txt',
        'templates/base.html',
        'templates/client.html',
        'templates/login.html',
        'templates/dashboard.html',
        'templates/client_dashboard.html',
        'static/styles.css',
        'static/optimized.js'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
        else:
            print(f"✅ File found: {file_path}")
    
    if missing_files:
        print(f"❌ Missing files: {', '.join(missing_files)}")
        return False
    
    return True

def configure_environment():
    """Set up environment variables"""
    # Set Flask environment
    os.environ.setdefault('FLASK_ENV', 'development')
    os.environ.setdefault('FLASK_DEBUG', '1')
    
    print("✅ Environment configured for development")

def start_application():
    """Start the Flask application"""
    port = int(os.environ.get("PORT", 5000))  # Railway provides PORT
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    
    print("\n🚀 Starting TechFlow Issue Tracking System...")
    print("=" * 50)
    print(f"📱 Application will be available at: http://localhost:{port}")
    print("👥 Default login credentials:")
    print("   Technical Team: admin / password123")
    print("   Client: any username / any password")
    print("=" * 50)
    print("Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        # Import and run the Flask app
        from app import app
        app.run(debug=debug, host='0.0.0.0', port=port)
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting application: {e}")
        return False
    
    return True

def main():
    """Main startup function"""
    print("🔧 TechFlow Issue Tracking System - Startup Check")
    print("=" * 50)
    
    # Run all checks
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Directories", create_directories),
        ("Files", check_files),
        ("Environment", configure_environment)
    ]
    
    all_passed = True
    for check_name, check_func in checks:
        print(f"\n🔍 Checking {check_name}...")
        if not check_func():
            all_passed = False
            print(f"❌ {check_name} check failed")
    
    if not all_passed:
        print("\n❌ Some checks failed. Please fix the issues above before starting the application.")
        return False
    
    print("\n✅ All checks passed! Starting application...")
    
    # Start the application
    return start_application()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

