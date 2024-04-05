#!/usr/bin/env bash
# Exit on error
set -o errexit

# Modify this line as needed for your package manager (pip, poetry, etc.)
#pip install -r requirements.txt




# Activate virtual environment if necessary
# This assumes your virtual environment directory is named 'venv'
# and located in the same directory as this script.
source .venv/Scripts/activate

# Ensure the correct Python version is being used
# This checks for Python version 3.8 as an example; adjust as needed.
REQUIRED_PY_VER="3.8"
if ! python -c "import sys; assert sys.version_info[:2] == (${REQUIRED_PY_VER//./,})" 2>/dev/null; then
    echo "This project requires Python $REQUIRED_PY_VER."
    exit 1
fi

# Install dependencies, excluding platform-specific ones on non-Windows systems
if [[ "$OSTYPE" == "win32" ]]; then
    pip install -r requirements.txt
else
    # Create a temporary requirements file that excludes pywin32
    grep -vE "pywin32" requirements.txt > temp_requirements.txt
    pip install -r temp_requirements.txt
    rm temp_requirements.txt
fi








# Convert static asset files
python manage.py collectstatic --no-input

# Apply any outstanding database migrations
python manage.py migrate