"""
Before running, remember to:
1. Run OpenHardwareMonitor
2. Activate python virutal environment: source env/Scripts/activate
"""
import wmi
import json

def get_pc(PARENT_CPU,PARENT_GPU):
   return ClassPC(PARENT_CPU, PARENT_GPU)

class ClassPC:
   def __init__(self, PARENT_CPU, PARENT_GPU):
      w = wmi.WMI(namespace=r"root\OpenHardwareMonitor")
      list_sensors = w.Sensor()
      assert len(list_sensors) > 0, "OpenHardwareMonitor.exe is not running!"

      dict_sensor = {}
      dict_sensor_json = {}
      # Groups sensors based on PC Components 
      for sensor in list_sensors:
         pc_sensor = ClassSensor.from_sensor(sensor)
         if sensor.Parent not in dict_sensor:
            dict_sensor[sensor.Parent] = {}
            dict_sensor_json[sensor.Parent] = {}
         if sensor.SensorType not in dict_sensor[sensor.Parent]:
            dict_sensor[sensor.Parent][sensor.SensorType] = {}
            dict_sensor_json[sensor.Parent][sensor.SensorType] = {}
         if sensor.Name not in dict_sensor[sensor.Parent][sensor.SensorType]:
            dict_sensor[sensor.Parent][sensor.SensorType][sensor.Name] = pc_sensor
            dict_sensor_json[sensor.Parent][sensor.SensorType][sensor.Name] = pc_sensor.value
         else:
            raise ValueError("Did not expect {} vs {}".format(dict_sensor[sensor.Parent][sensor.SensorType][sensor.Name], pc_sensor))     
      
      # Print to debug
      # print("SENSORS: {}".format(json.dumps(dict_sensor_json)))

      if PARENT_CPU not in dict_sensor_json or PARENT_GPU not in dict_sensor_json:
         raise ValueError("Either $PARENT_CPU=\"{}\" or $PARENT_GPU=\"{}\" is not found in \"{}\"!".format(PARENT_CPU, PARENT_GPU, json.dumps(list(dict_sensor_json.keys()))))
      
      cpu_sensor = dict_sensor[PARENT_CPU]
      gpu_sensor = dict_sensor[PARENT_GPU]
      ram_sensor = dict_sensor["/ram"]
      # hdd_sensor = dict_sensor["/hdd/0"]

      # assert dict_sensor[sensor.Name]
      self.cpu = ClassComponent.from_Sensors('CPU', cpu_sensor)
      self.gpu = ClassComponent.from_Sensors('GPU', gpu_sensor)
      self.ram = ClassComponent.from_Sensors('RAM', ram_sensor)
      # self.disk = ClassComponent.from_Sensors('HDD', hdd_sensor)
   
   def print_status(self):
      # CPU Status
      print("CPU POWER: {0:.2f} W "              .format(self.cpu.get_power()      ))
      print("CPU TEMP : {0:.2f} \N{DEGREE SIGN}C".format(self.cpu.get_temperature()))
      print("CPU LOAD : {0:.2f} % "              .format(self.cpu.get_load()       ))
      # GPU Status
      print("GPU POWER: {0:.2f} W "              .format(self.gpu.get_power()      ))
      print("GPU TEMP : {0:.2f} \N{DEGREE SIGN}C".format(self.gpu.get_temperature()))
      print("GPU LOAD : {0:.2f} % "              .format(self.gpu.get_load()       ))
      # RAM Status
      print("RAM LOAD : {0:.2f} %"               .format(self.ram.get_load()       ))
      print("RAM USAGE: {0:.2f}/{1:.2f} GB"      .format(self.ram.get_memory_used(), self.ram.get_memory_used() + self.ram.get_memory_available()))

   def send_status(self, COMPUTER_NAME, statsd_client):
      # CPU Status
      statsd_client.gauge('{}.cpu.power'.format(COMPUTER_NAME)      , self.cpu.get_power()      )
      statsd_client.gauge('{}.cpu.temperature'.format(COMPUTER_NAME), self.cpu.get_temperature())
      statsd_client.gauge('{}.cpu.load'.format(COMPUTER_NAME)       , self.cpu.get_load()       )
      # GPU Status
      statsd_client.gauge('{}.gpu.power'.format(COMPUTER_NAME)      , self.gpu.get_power()      )
      statsd_client.gauge('{}.gpu.temperature'.format(COMPUTER_NAME), self.gpu.get_temperature())
      statsd_client.gauge('{}.gpu.load'.format(COMPUTER_NAME)       , self.gpu.get_load()       )
      # RAM Status
      statsd_client.gauge('{}.ram.memory_used'.format(COMPUTER_NAME)      , self.ram.get_memory_used()      )
      statsd_client.gauge('{}.ram.memory_available'.format(COMPUTER_NAME), self.ram.get_memory_available())
      statsd_client.gauge('{}.ram.load'.format(COMPUTER_NAME)       , self.ram.get_load()       )

class ClassComponent:
   def __init__(self, name, sensor_power, sensor_temperature, sensor_load, sensor_used, sensor_available):
      self.name = name
      self.sensor_power = sensor_power
      self.sensor_temperature = sensor_temperature
      self.sensor_load = sensor_load
      self.sensor_used = sensor_used
      self.sensor_available = sensor_available
   
   @classmethod
   def from_Sensors(cls, name, dict_sensor):
      sensor_power       = None # Used by CPU, GPU
      sensor_temperature = None # Used by CPU, GPU
      sensor_load        = None # Used by CPU, CPU, RAM
      sensor_used        = None # Used by RAM
      sensor_available   = None # Used by RAM

      if name == "CPU":
         sensor_power       = dict_sensor["Power"      ]["CPU Package"]
         sensor_temperature = dict_sensor["Temperature"]["CPU Package"]
         sensor_load        = dict_sensor["Load"       ]["CPU Total"  ]
      elif name == "GPU":
         sensor_power       = dict_sensor["Power"      ]["GPU Total" ]
         sensor_temperature = dict_sensor["Temperature"]["GPU Core" ]
         sensor_load        = dict_sensor["Load"       ]["GPU Core"]
      elif name == "RAM":
         sensor_used      = dict_sensor["Data"]["Used Memory"     ]
         sensor_available = dict_sensor["Data"]["Available Memory"]
         sensor_load      = dict_sensor["Load"]["Memory"          ]
      elif name == "HDD":
         raise NotImplementedError()
         # sensor_temperature = dict_sensor["Temperature"]["Temperature" ]
         # sensor_load        = dict_sensor["Load"       ]["Used Space"  ]
      else:
         raise ValueError("Did not expect: {}".format(name))
      return cls(name, sensor_power, sensor_temperature, sensor_load, sensor_used, sensor_available)
   
   def get_power(self):
      """
      Returns power in Watts (W)
      """
      return self.sensor_power.value

   def get_temperature(self):
      """
      Returns temperature in Celsius (C)
      """
      return self.sensor_temperature.value
      
   def get_load(self):
      """
      Returns load in percentage (%)
      """
      return self.sensor_load.value
   
   def get_memory_used(self):
      """
      Returns memory used in GB
      """
      return self.sensor_used.value
   
   def get_memory_available(self):
      """
      Returns memory available in GB
      """
      return self.sensor_available.value

class ClassSensor:
   def __init__(self, name, uid, stype, value):
      self.name  = name
      self.uid   = uid
      self.stype = stype
      self.value = value

   @classmethod
   def from_sensor(cls, sensor):
      """
         Example data:

         instance of Sensor
         {
               Identifier = "/amdcpu/0/power/0";
               Index = 0;
               InstanceId = "xxxx";
               Max = 48.48785;
               Min = 32.04075;
               Name = "CPU Package";
               Parent = "/amdcpu/0";
               ProcessId = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx";
               SensorType = "Power";
               Value = 33.0748;
         };

         instance of Sensor
         {
               Identifier = "/atigpu/0/load/0";
               Index = 0;
               InstanceId = "xxxx";
               Max = 9;
               Min = 0;
               Name = "GPU Core";
               Parent = "/atigpu/0";
               ProcessId = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx";
               SensorType = "Load";
               Value = 0;
         };
      """
      name  = sensor.Name      
      uid   = sensor.Identifier
      stype = sensor.SensorType
      value = sensor.Value
      return cls(name, uid, stype, value)
   
   def __str__(self):
      return "name: {}, uid: {}, stype: {}, value:{}".format(self.name, self.uid, self.stype, self.value)

