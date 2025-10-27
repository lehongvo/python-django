# Virtual Environments and Package Management

## What is a Virtual Environment?

A virtual environment is an isolated Python environment that allows you to work on a specific project without interfering with other projects. Each virtual environment has its own installed packages and dependencies.

## Why Use Virtual Environments?

- **Isolation**: Keep dependencies for each project separate
- **Version Control**: Use different versions of packages for different projects
- **Reproducibility**: Easily recreate the same environment
- **Clean System**: Keep your global Python installation clean

## Creating a Virtual Environment

### Method 1: Using venv (Recommended)

```bash
# Create a virtual environment
python3 -m venv myenv

# Activate virtual environment
# On macOS/Linux:
source myenv/bin/activate

# On Windows:
myenv\Scripts\activate

# Deactivate virtual environment
deactivate
```

### Method 2: Using virtualenv

```bash
# Install virtualenv first
pip install virtualenv

# Create virtual environment
virtualenv myenv

# Activate virtual environment
source myenv/bin/activate  # macOS/Linux
myenv\Scripts\activate    # Windows
```

### Method 3: Using conda (if you have Anaconda/Miniconda)

```bash
# Create environment
conda create -n myenv python=3.11

# Activate environment
conda activate myenv

# Deactivate
conda deactivate
```

## Package Management with pip

### Installing Packages

```bash
# Install a package
pip install django

# Install specific version
pip install django==4.2.0

# Install from requirements.txt
pip install -r requirements.txt

# Upgrade a package
pip install --upgrade django

# Uninstall a package
pip uninstall django
```

### Creating requirements.txt

```bash
# Generate requirements.txt from current environment
pip freeze > requirements.txt

# Install from requirements.txt
pip install -r requirements.txt
```

### Example requirements.txt

```txt
Django==4.2.0
djangorestframework==3.14.0
python-decouple==3.8
psycopg2-binary==2.9.6
Pillow==10.0.0
```

## Common pip Commands

```bash
# List installed packages
pip list

# Show package information
pip show django

# Search for packages
pip search django

# Install packages in development mode (editable)
pip install -e .

# Check for outdated packages
pip list --outdated

# Upgrade all packages
pip install --upgrade -r requirements.txt
```

## Best Practices

1. **Always use virtual environments** for each project
2. **Never commit** your `venv` or `env` folder to git
3. **Always create requirements.txt** to track dependencies
4. **Use `.gitignore`** to exclude virtual environment folders
5. **Specify versions** in requirements.txt for reproducibility

## Virtual Environment Workflow

```bash
# 1. Create project directory
mkdir myproject
cd myproject

# 2. Create virtual environment
python3 -m venv venv

# 3. Activate virtual environment
source venv/bin/activate

# 4. Install packages
pip install django

# 5. Freeze requirements
pip freeze > requirements.txt

# 6. When done, deactivate
deactivate
```

## Python Version Management

### Using pyenv (Recommended for managing Python versions)

```bash
# Install pyenv (macOS)
brew install pyenv

# Install specific Python version
pyenv install 3.11.0

# Set local version for project
pyenv local 3.11.0

# List installed versions
pyenv versions

# Uninstall version
pyenv uninstall 3.10.0
```

## Troubleshooting

### Common Issues

1. **Command not found after activation**
   - Make sure you're using `source venv/bin/activate`
   - Check that the activation script exists

2. **Wrong Python version**
   - Use `python3 -m venv venv` instead of `python -m venv venv`
   - Check Python version with `python --version`

3. **Package installation fails**
   - Update pip: `pip install --upgrade pip`
   - Check Python version compatibility

4. **Virtual environment not isolated**
   - Make sure you activate it before installing packages
   - Verify with `which python` (should show venv path)

