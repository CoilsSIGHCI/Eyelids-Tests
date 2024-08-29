import asyncio
import tkinter as tk
from tkinter import ttk, messagebox
from bleak import BleakScanner, BleakClient

class BluetoothConnector:
    def __init__(self):
        self.client = None
        self.connected_device = None

    async def scan_for_devices(self):
        devices = await BleakScanner.discover()
        return devices

    async def connect_to_device(self, device):
        self.client = BleakClient(device.address)
        try:
            await self.client.connect()
            self.connected_device = device
            return True
        except Exception as e:
            print(f"Connection error: {e}")
            return False

    async def disconnect(self):
        if self.client:
            await self.client.disconnect()
            self.client = None
            self.connected_device = None

    async def get_services(self):
        if not self.client:
            return None
        return await self.client.get_services()

    async def read_characteristic(self, char_uuid):
        if not self.client:
            raise Exception("Not connected to any device")
        return await self.client.read_gatt_char(char_uuid)

    async def write_characteristic(self, char_uuid, data):
        if not self.client:
            raise Exception("Not connected to any device")
        await self.client.write_gatt_char(char_uuid, data)

class BluetoothGUI:
    def __init__(self, master):
        self.master = master
        self.connector = BluetoothConnector()
        master.title("Bluetooth Device Connector")
        master.geometry("400x300")

        self.scan_button = ttk.Button(master, text="Scan for Devices", command=self.start_scan)
        self.scan_button.pack(pady=10)

        self.device_listbox = tk.Listbox(master, width=50)
        self.device_listbox.pack(pady=10)

        self.connect_button = ttk.Button(master, text="Connect", command=self.connect_to_device, state=tk.DISABLED)
        self.connect_button.pack(pady=10)

        self.status_label = ttk.Label(master, text="")
        self.status_label.pack(pady=10)

        self.devices = []

    def start_scan(self):
        self.scan_button.config(state=tk.DISABLED)
        self.device_listbox.delete(0, tk.END)
        self.status_label.config(text="Scanning...")
        self.master.after(100, self.perform_scan)

    def perform_scan(self):
        asyncio.run(self._scan_for_devices())

    async def _scan_for_devices(self):
        self.devices = await self.connector.scan_for_devices()
        for i, device in enumerate(self.devices):
            self.device_listbox.insert(tk.END, f"{device.name or 'Unknown'} ({device.address})")
        self.scan_button.config(state=tk.NORMAL)
        self.connect_button.config(state=tk.NORMAL)
        self.status_label.config(text="Scan complete")

    def connect_to_device(self):
        selection = self.device_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a device")
            return
        selected_index = selection[0]
        selected_device = self.devices[selected_index]
        self.status_label.config(text=f"Connecting to {selected_device.name or 'Unknown'}...")
        self.master.after(100, lambda: self.perform_connection(selected_device))

    def perform_connection(self, device):
        asyncio.run(self._connect_and_interact(device))

    async def _connect_and_interact(self, device):
        if await self.connector.connect_to_device(device):
            self.status_label.config(text="Connected!")
            services = await self.connector.get_services()
            service_info = "Services:\n"
            for service in services:
                service_info += f"Service: {service.uuid}\n"
                for char in service.characteristics:
                    service_info += f"  Characteristic: {char.uuid}\n"
                    service_info += f"    Properties: {', '.join(char.properties)}\n"
            messagebox.showinfo("Device Information", service_info)
        else:
            self.status_label.config(text="Connection failed")

def run_gui():
    root = tk.Tk()
    app = BluetoothGUI(root)
    root.mainloop()

if __name__ == "__main__":
    run_gui()
