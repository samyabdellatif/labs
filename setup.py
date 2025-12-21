#!/usr/bin/env python3
"""
Setup script for Laboratory Schedule Management System
This script helps users set up the project environment
"""

import os
import sys
import subprocess
import secrets

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ Error in {description}: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python version {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def create_virtual_environment():
    """Create Python virtual environment"""
    if os.path.exists('venv'):
        print("✅ Virtual environment already exists")
        return True
    
    return run_command("python -m venv venv", "Creating virtual environment")

def create_env_file():
    """Create .env file from template"""
    if os.path.exists('.env'):
        print("✅ .env file already exists")
        return True
    
    if not os.path.exists('.env.example'):
        print("❌ .env.example file not found")
        return False
    
    # Read template and generate secret key
    with open('.env.example', 'r') as f:
        content = f.read()
    
    # Generate a secure secret key
    secret_key = secrets.token_hex(32)
    content = content.replace('your-secure-secret-key-here', secret_key)
    
    # Write to .env file
    with open('.env', 'w') as f:
        f.write(content)
    
    print("✅ Created .env file with generated secret key")
    print("⚠️  Please update MONGO_URI in .env file with your MongoDB connection string")
    return True

def install_dependencies():
    """Install Python dependencies"""
    if not os.path.exists('requirements.txt'):
        print("❌ requirements.txt file not found")
        return False
    
    # Use python -m pip which works reliably across platforms
    if os.name == 'nt':  # Windows
        pip_command = "venv\\Scripts\\python.exe -m pip"
    else:  # macOS/Linux
        pip_command = "venv/bin/python -m pip"
    
    return run_command(f"{pip_command} install -r requirements.txt", "Installing dependencies")

def main():
    """Main setup function"""
    print("🚀 Setting up Laboratory Schedule Management System")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create virtual environment
    if not create_virtual_environment():
        sys.exit(1)
    
    # Create .env file
    if not create_env_file():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Update MONGO_URI in .env file with your MongoDB connection string")
    print("2. Activate virtual environment:")
    print("   - Windows: venv\\Scripts\\activate")
    print("   - macOS/Linux: source venv/bin/activate")
    print("3. Run the application: python server.py")
    print("4. Open browser and go to: http://127.0.0.1:5000")
    print("\n🔐 Default login: username 'admin', password 'password'")
    print("\n📚 For detailed instructions, see README.md")

if __name__ == "__main__":
    main()
