#!/usr/bin/env python3
"""
Setup verification script
Checks that all dependencies are properly configured
"""
import sys


def check_imports():
    """Check if all required packages can be imported"""
    print("🔍 Checking Python dependencies...\n")
    
    required_packages = {
        'fastapi': 'FastAPI',
        'uvicorn': 'Uvicorn',
        'telegram': 'python-telegram-bot',
        'web3': 'Web3.py',
        'supabase': 'Supabase',
        'dotenv': 'python-dotenv',
        'pydantic': 'Pydantic',
        'pydantic_settings': 'Pydantic Settings',
        'eth_account': 'eth-account',
    }
    
    failed = []
    
    for package, name in required_packages.items():
        try:
            __import__(package)
            print(f"✅ {name}")
        except ImportError:
            print(f"❌ {name} - NOT FOUND")
            failed.append(name)
    
    if failed:
        print(f"\n❌ Missing dependencies: {', '.join(failed)}")
        print("\nInstall missing packages with:")
        print("pip install -r requirements.txt")
        return False
    
    print("\n✅ All dependencies installed!")
    return True


def check_env_file():
    """Check if .env file exists"""
    print("\n🔍 Checking environment configuration...\n")
    
    import os
    
    if os.path.exists('.env'):
        print("✅ .env file found")
        return True
    else:
        print("⚠️  .env file not found")
        print("\nCreate .env file from template:")
        print("cp .env.example .env")
        print("\nThen edit .env and fill in your credentials.")
        return False


def check_modules():
    """Check if all modules can be imported"""
    print("\n🔍 Checking application modules...\n")
    
    modules = [
        'config',
        'database',
        'safe_service',
        'telegram_bot',
        'api',
        'cli',
        'main'
    ]
    
    # We need a .env file to import modules
    import os
    if not os.path.exists('.env'):
        print("⚠️  Cannot check modules without .env file")
        return False
    
    failed = []
    
    for module in modules:
        try:
            __import__(module)
            print(f"✅ {module}.py")
        except Exception as e:
            print(f"❌ {module}.py - ERROR: {str(e)[:50]}")
            failed.append(module)
    
    if failed:
        print(f"\n❌ Failed to import: {', '.join(failed)}")
        return False
    
    print("\n✅ All modules can be imported!")
    return True


def main():
    """Main setup verification"""
    print("=" * 60)
    print("Treasury Sentinel - Setup Verification")
    print("=" * 60)
    print()
    
    results = []
    
    # Check dependencies
    results.append(check_imports())
    
    # Check environment file
    results.append(check_env_file())
    
    # Only check modules if basic setup is done
    if all(results):
        results.append(check_modules())
    
    print("\n" + "=" * 60)
    if all(results):
        print("✅ Setup verification PASSED!")
        print("\nYou can now run the application:")
        print("  python main.py")
        print("\nOr use the CLI:")
        print("  python cli.py --help")
        print("=" * 60)
        sys.exit(0)
    else:
        print("❌ Setup verification FAILED!")
        print("\nPlease fix the issues above and run this script again.")
        print("=" * 60)
        sys.exit(1)


if __name__ == '__main__':
    main()
