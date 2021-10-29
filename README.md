# Yrden

Yrden is a DFR tool plugin manager which is used to manage plugins that will gather potential digital evidenve (PDE) proactively.
It is designed to aid in the overall digital forensic investigation (DFI) process by making it easier to adopt a system that can gather PDE.

The tools used for Yrden should be adapted to work like the examples in the repository and requires the following components:
- main.py -> used to run the plugin via the Yrden core system
- requirements.txt -> tell the Yrden core system which dependencies are required
- config.txt -> includes url where to store the PDE
- core -> directory that includes the core functionality of the plugin

## Installation

Yrden was built with Python 3.10 and should work on both Windows and Linux (Mac is not tested). It is recommended that you run this tool in a Python 3.10 virtual environment.

```
git clone git@github.com:ICFL-UP/Yrden.git
cd Yrden
python3.10 -m venv venv
source venv/bin/activate # Linux
source venv/scripts/activate # Windows
pip install -r requirements.txt
```

## Usage

```
python manage.py makemigrations   # creates the database scripts
python manage.py migrate          # migrates the database scripts into the db
python manage.py createsuperuser  # creates a superuser for the admin section
python manage.py runserver
```

Note: To access the system you have to go to the following address -> ```http://localhost:8000/core```

## Running Plugins

The tool is designed to run the tools periodically without any user interaction. This requires a cronjob to be setup so that the computer can execute the plugins.


You can also run the plugins manually by using the following management command:
```
python manage.py run_plugins
```
