import asyncio
import tkinter as tk
from tkinter import ttk, messagebox
from bleak import BleakScanner, BleakClient

class BluetoothConnector:
    def __init__(self):
        self.client: BleakClient = None
        self.connected_device = None
        self.eyelids_service_uuid = "D57D86F6-E6F3-4BE4-A3D1-A71119D27AD3"
        self.animation_control_uuid = "4116f8d2-9f66-4f58-a53d-fc7440e7c14e"

    async def scan_for_devices(self):
        devices = await BleakScanner.discover(
            return_adv=True,
            service_uuids=[self.eyelids_service_uuid]
        )
        return [device for device, adv_data in devices.values()]

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

    async def write_characteristic(self, data):
        if not self.client:
            raise Exception("Not connected to any device")
        await self.client.write_gatt_char(self.animation_control_uuid, data)

    async def eyelids_direction(self, direction):
        if not self.client:
            raise Exception("Not connected to Eyelids device")
        pattern = self.get_eyelids_pattern(direction)
        print(f"Writing pattern: {pattern}")
        await self.write_characteristic(pattern.encode())

    def get_eyelids_pattern(self, direction):
        patterns = {
            "Forward": "NAV_FORWARD",
            "Backward": "NAV_BACKWARD",
            "Left": "NAV_LEFT",
            "Right": "NAV_RIGHT",
            "Stop": "NAV_STOP"
        }
        return patterns.get(direction, "OFF")

class BluetoothGUI:
    def __init__(self, master, loop):
        self.master = master
        self.loop = loop
        self.connector = BluetoothConnector()
        master.title("Eyelids Device Connector")
        master.geometry("400x350")

        self.scan_button = ttk.Button(master, text="Scan for Eyelids Devices", command=self.start_scan)
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
        self.status_label.config(text="Scanning for Eyelids devices...")
        self.loop.create_task(self._scan_for_devices())

    async def _scan_for_devices(self):
        self.devices = await self.connector.scan_for_devices()
        for i, device in enumerate(self.devices):
            self.device_listbox.insert(tk.END, f"{device.name or 'Unknown Eyelids Device'} ({device.address})")
        self.scan_button.config(state=tk.NORMAL)
        self.connect_button.config(state=tk.NORMAL if self.devices else tk.DISABLED)
        self.status_label.config(text="Scan complete" if self.devices else "No Eyelids devices found")

    def connect_to_device(self):
        selection = self.device_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an Eyelids device")
            return
        selected_index = selection[0]
        selected_device = self.devices[selected_index]
        self.status_label.config(text=f"Connecting to {selected_device.name or 'Unknown Eyelids Device'}...")
        self.loop.create_task(self._connect_and_interact(selected_device))

    async def _connect_and_interact(self, device):
        if await self.connector.connect_to_device(device):
            self.status_label.config(text="Connected to Eyelids device!")
        else:
            self.status_label.config(text="Connection to Eyelids device failed")

def run_gui(loop):
    root = tk.Tk()
    app = BluetoothGUI(root, loop)

    def update_gui():
        root.update()
        loop.call_later(0.05, update_gui)

    loop.call_soon(update_gui)
    loop.run_forever()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    run_gui(loop)
