
OPTIONS = {'comm': 'COM1','speed': '115200','parity': 'None','databit': '8','stopbit': '1','dhcp': 1,
           'ip': '192.168.0.5', 'subnet': '255.255.255.0', 'gateway': '192.168.0.1', 'port': '5000',
           'peer_ip': '192.168.0.6', 'peer_port': '5000', 'host_ip': '192.168.0.2', 'host_port': '5000',
           'key': '12345678'}

def read_ui_options(self):
    options = {}
    options['comm'] = self.entry_serial_port.get()
    options['speed'] = self.entry_serial_speed.get()
    options['parity'] = self.entry_serial_parity.get()
    options['databit'] = self.entry_serial_databit.get()
    options['stopbit'] = self.entry_serial_stopbit.get()

    if self.switch_var.get() == "DHCP":
        options['dhcp'] = 1
    else:
        options['dhcp'] = 0
    options['ip'] = self.entry_ip.get()
    options['subnet'] = self.entry_subnet.get()
    options['gateway'] = self.entry_gateway.get()
    options['port'] = self.entry_port.get()

    options['peer_ip'] = self.entry_peer_ip.get()
    options['peer_port'] = self.entry_peer_port.get()
    options['host_ip'] = self.entry_host_ip.get()
    options['host_port'] = self.entry_host_port.get()

    options['key'] = self.entry_key.get()

    return options

def apply_ui_options(self, options):
    if options['dhcp'] and self.switch_var.get() == "NO-DHCP":
        self.switch_var.set("DHCP")
        self.dhcp_event()
        self.entry_ip.configure(state='normal')
        self.entry_gateway.configure(state='normal')
        self.entry_subnet.configure(state='normal')

        self.entry_ip.delete(0, "end")
        self.entry_ip.insert(0, options["ip"])
        self.entry_gateway.delete(0, "end")
        self.entry_gateway.insert(0, options["gateway"])
        self.entry_subnet.delete(0, "end")
        self.entry_subnet.insert(0, options["subnet"])

        #self.entry_ip.configure(state='disabled')
        #self.entry_gateway.configure(state='disabled')
        #self.entry_subnet.configure(state='disabled')
    elif not options['dhcp'] and self.switch_var.get() == "DHCP":
        self.switch_var.set("NO-DHCP")
        self.dhcp_event()

        self.entry_ip.delete(0, "end")
        self.entry_ip.insert(0, options["ip"])
        self.entry_gateway.delete(0, "end")
        self.entry_gateway.insert(0, options["gateway"])
        self.entry_subnet.delete(0, "end")
        self.entry_subnet.insert(0, options["subnet"])
    else:
        self.entry_ip.configure(state='normal')
        self.entry_gateway.configure(state='normal')
        self.entry_subnet.configure(state='normal')

        self.entry_ip.delete(0, "end")
        self.entry_ip.insert(0, options["ip"])
        self.entry_gateway.delete(0, "end")
        self.entry_gateway.insert(0, options["gateway"])
        self.entry_subnet.delete(0, "end")
        self.entry_subnet.insert(0, options["subnet"])

        #self.entry_ip.configure(state='disabled')
        #self.entry_gateway.configure(state='disabled')
        #self.entry_subnet.configure(state='disabled')

    self.entry_port.delete(0, "end")
    self.entry_port.insert(0, options["port"])
    self.entry_key.delete(0, "end")
    self.entry_key.insert(0, options["key"])

def read_options_file(self):
    options = {}

    with open("k2_config.txt", "r") as f:
        lines = f.readlines()
        options['comm'] = lines[0].split("comm:")[1].strip()
        dhcp =  lines[1].split("dhcp:")[1].strip()
        if dhcp == 'true':
            options['dhcp'] = 1
        else:
            options['dhcp'] = 0
        options['ip'] = lines[2].split("ip:")[1].strip()
        options['gateway'] = lines[3].split("gateway:")[1].strip()
        options['subnet'] = lines[4].split("subnet:")[1].strip()
        options['port'] = lines[5].split("port:")[1].strip()
        options['key'] = lines[6].split("key:")[1].strip()

    return options

def write_options_file(self, options):
    with open('k2_config.txt', 'w') as f:
        f.write("comm:" + options["comm"] + "\n")
        if options["dhcp"]:
            f.write("dhcp:" + 'true' + "\n")
        else:
            f.write("dhcp:" + 'false' + "\n")
        f.write("ip:" + options["ip"] + "\n")
        f.write("gateway:" + options["gateway"] + "\n")
        f.write("subnet:" + options["subnet"] + "\n")
        f.write("port:" + options["port"] + "\n")
        f.write("key:" + options["key"] + "\n")
