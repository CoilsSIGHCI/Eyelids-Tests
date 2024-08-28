import asyncio
from bleak import BleakScanner, BleakClient

async def select_and_connect_bluetooth():
    print("Scanning for Bluetooth devices...")
    devices = await BleakScanner.discover()

    if not devices:
        print("No devices found.")
        return

    print("Available devices:")
    for i, device in enumerate(devices):
        print(f"{i+1}. {device.name or 'Unknown'} ({device.address})")

    selection = int(input("Select a device number: ")) - 1
    selected_device = devices[selection]

    print(f"Connecting to {selected_device.name or 'Unknown'}...")
    async with BleakClient(selected_device.address) as client:
        try:
            await client.connect()
            print("Connected!")

            # Discover services and characteristics
            services = await client.get_services()
            for service in services:
                print(f"Service: {service.uuid}")
                for char in service.characteristics:
                    print(f"  Characteristic: {char.uuid}")
                    print(f"    Properties: {', '.join(char.properties)}")

            # Here you can interact with the device using GATT operations
            # For example, to read a characteristic:
            # value = await client.read_gatt_char("CHARACTERISTIC_UUID")
            # Or to write to a characteristic:
            # await client.write_gatt_char("CHARACTERISTIC_UUID", b"data")

        except Exception as e:
            print(f"Error: {e}")
        finally:
            await client.disconnect()
            print("Disconnected")

asyncio.run(select_and_connect_bluetooth())
