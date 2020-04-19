# Hardware Sensor Logging for Windows 10
Send hardware info to graphana via statsd

## Prerequisites
### Install
1. Setup Graphana and Graphite with StatsD Server
    - Setup graphite [link1](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-graphite-on-an-ubuntu-14-04-server) [link2](https://www.snel.com/support/how-to-install-grafana-graphite-and-statsd-on-ubuntu-18-04/)
    - Setup statsD [link1](https://www.digitalocean.com/community/tutorials/how-to-configure-statsd-to-collect-arbitrary-stats-for-graphite-on-ubuntu-14-04)
    - CollectD is not necessary, I did not install it.
2. Python 3, I was using `version 3.8.2` [link](https://www.python.org/downloads/)
3. Git, I was using ` version 2.26.0.windows.1` [link](https://git-scm.com/download/win)
4. OpenHardwareMonitor, the script obtains reading from this using wmi [link](https://openhardwaremonitor.org/)

### External Python Libraries
Update PIP
```
python -m pip install --upgrade pip
```
Install required libraries
```
pip install virtualenv
```

## Setup
### Workspace Creation 
Navigate to new workspace folder
```
cd path/to/workspace
```

### Download from Git
```
git clone https://github.com/Palt0n/kh-serverstats.git
```

### Setup python virtual environment with venv
Create python virtual enviroment with venv
```
python -m venv env
```
To activate venv
```
source env/Scripts/activate
```
To check if venv is activated

```
which python
```
- This command should return the path for python.
- This path should be located in the local env folder

If you want to exit venv later (DONT EXIT NOW!), use
```
deactivate
```
### Download external python libraries
Have to repeat the pip upgrade in venv
```
python -m pip install --upgrade pip
```

Ensure that venv is activated, then install the libararies using pip
```
pip install -r requirements.txt
```
Or run 
```
pip install statsd
pip install psutil
pip install wmi
pip install pypiwin32
```

## Enviroment Variables
Either manually set in the terminal using
```
SERVER_IP="127.0.0.1"
export SERVER_IP

PARENT_CPU="//amdcpu/0"
export PARENT_CPU

PARENT_GPU="//atigpu/0"
export PARENT_GPU

COMPUTER_NAME="desktop_my"
export COMPUTER_NAME
```
For $PARENT_CPU and $PARENT_GPU, the double // is necessary to prevent windows from interpreting the single slash as root directory

Or edit the `env\Scripts\activate.bat`
```
set SERVER_IP=127.0.0.1
set PARENT_CPU=//amdcpu/0
set PARENT_GPU=//atigpu/0
set COMPUTER_NAME=desktop_erwin
```
## Run
```
python send_statsd.py
```
If got error
```
wmi.x_wmi: <x_wmi: Unexpected COM Error (XXXXXXX), None, None>
```
It means you didn't install/run OpenHardwareMonitor yet
## Developer Misc
### Create requirements.txt file
```
pip freeze > requirements.txt
```
### Powershell loop every 10 seconds
Create .bat file
```
cd C:\path\to\workspace && env\Scripts\activate.bat && python send_statsd.py && deactivate
```
Run .bat file
```
while(1)
>> {
>> C:\path\to\workspace.bat
>> timeout /t 10
>> }
```