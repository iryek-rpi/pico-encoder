
OPTIONS = {'comm': 'COM1','speed': '115200','parity': 'None','data': '8','stop': '1',
           'ip': '192.168.0.5', 'subnet': '255.255.255.0', 'gateway': '192.168.0.1', 
           'peer_ip': '192.168.0.6', 'host_ip': '192.168.0.2', 'host_port': '5000',
           'channel': 0,
           'key': '12345678'}

def read_ui_options(self):
    options = {}
    options['comm'] = self.entry_serial_port.get()
    options['speed'] = self.entry_serial_speed.get()
    options['parity'] = self.entry_serial_parity.get()
    options['data'] = self.entry_serial_data.get()
    options['stop'] = self.entry_serial_stop.get()

    options['ip'] = self.entry_ip.get()
    options['subnet'] = self.entry_subnet.get()
    options['gateway'] = self.entry_gateway.get()

    options['peer_ip'] = self.entry_peer_ip.get()
    options['host_ip'] = self.entry_host_ip.get()
    options['host_port'] = self.entry_host_port.get()

    options['channel'] = 1 if self.channel_var.get() == "TCP" else 0
    options['key'] = self.entry_key.get()

    return options

def apply_ui_options(self, options):
    self.entry_serial_port.delete(0, "end")
    self.entry_serial_port.insert(0, options["comm"])
    self.entry_serial_speed.delete(0, "end")
    self.entry_serial_speed.insert(0, options["speed"])
    self.entry_serial_parity.delete(0, "end")
    self.entry_serial_parity.insert(0, options["parity"])
    self.entry_serial_data.delete(0, "end")
    self.entry_serial_data.insert(0, options["data"])
    self.entry_serial_stop.delete(0, "end")
    self.entry_serial_stop.insert(0, options["stop"])
    
    self.entry_ip.delete(0, "end")
    self.entry_ip.insert(0, options["ip"])
    self.entry_gateway.delete(0, "end")
    self.entry_gateway.insert(0, options["gateway"])
    self.entry_subnet.delete(0, "end")
    self.entry_subnet.insert(0, options["subnet"])

    self.entry_peer_ip.delete(0, "end")
    self.entry_peer_ip.insert(0, options["peer_ip"])
    self.entry_host_ip.delete(0, "end")
    self.entry_host_ip.insert(0, options["host_ip"])
    self.entry_host_port.delete(0, "end")
    self.entry_host_port.insert(0, options["host_port"])

    self.entry_key.delete(0, "end")
    self.entry_key.insert(0, options["key"])

def read_options_file(self):
    options = {}

    with open("k2_config.txt", "r") as f:
        lines = f.readlines()
        options['comm'] = lines[0].split("comm:")[1].strip()
        options['speed'] = lines[1].split("speed:")[1].strip()
        options['parity'] = lines[2].split("parity:")[1].strip()
        options['data'] = lines[3].split("data:")[1].strip()
        options['stop'] = lines[4].split("stop:")[1].strip()

        options['ip'] = lines[6].split("ip:")[1].strip()
        options['gateway'] = lines[7].split("gateway:")[1].strip()
        options['subnet'] = lines[8].split("subnet:")[1].strip()

        options['peer_ip'] = lines[9].split("peer_ip:")[1].strip()
        options['host_ip'] = lines[10].split("host_ip:")[1].strip()
        options['host_port'] = lines[11].split("host_port:")[1].strip()

        options['channel'] = lines[12].split("channel:")[1].strip()

        options['key'] = lines[13].split("key:")[1].strip()

    return options

def write_options_file(self, options):
    with open('k2_config.txt', 'w') as f:
        f.write("comm:" + options["comm"] + "\n")
        f.write("speed:" + options["speed"] + "\n")
        f.write("parity:" + options["parity"] + "\n")
        f.write("data:" + options["data"] + "\n")
        f.write("stop:" + options["stop"] + "\n")

        f.write("ip:" + options["ip"] + "\n")
        f.write("gateway:" + options["gateway"] + "\n")
        f.write("subnet:" + options["subnet"] + "\n")

        f.write("peer_ip:" + options["peer_ip"] + "\n")
        f.write("host_ip:" + options["host_ip"] + "\n")
        f.write('host_port:' + options["host_port"] + "\n")

        f.write('channel:' + str(options["channel"]) + "\n")
        f.write("key:" + options["key"] + "\n")
