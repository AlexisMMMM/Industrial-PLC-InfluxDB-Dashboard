from pymodbus.client import ModbusTcpClient
from influxdb_client import InfluxDBClient, WriteOptions
from influxdb_client.client.write_api import SYNCHRONOUS
import time as time_module
from datetime import datetime, timezone

# ── Conexión al PLC (sin cambios) ─────────────────────────────────────────────
plc = ModbusTcpClient(host='127.0.0.1', port=502)

# ── Conexión a InfluxDB 2.7 ───────────────────────────────────────────────────
INFLUX_TOKEN = "TU_TOKEN_AQUI"
INFLUX_ORG   = "plc_org"
INFLUX_BUCKET = "plc_data"

influx = InfluxDBClient(
    url="http://localhost:8086",
    token=INFLUX_TOKEN,
    org=INFLUX_ORG
)
write_api = influx.write_api(write_options=SYNCHRONOUS)

def main():
    if not plc.connect():
        print("Error: No se pudo conectar al PLC")
        return

    print("Conectado al PLC — escribiendo a InfluxDB 2.7...")
    print("-" * 40)

    try:
        while True:
            sensor = plc.read_coils(address=0, count=1)
            motor  = plc.read_discrete_inputs(address=0, count=1)

            sensor_val = 1 if sensor.bits[0] else 0
            motor_val  = 1 if motor.bits[0]  else 0

            timestamp = datetime.now(timezone.utc)

            data = {
                "measurement": "conveyor_belt",
                "tags": {"node": "plc-node"},
                "fields": {
                    "sensor_object": sensor_val,
                    "motor_running":  motor_val
                },
                "time": timestamp
            }
            write_api.write(bucket=INFLUX_BUCKET, record=data)

            print(f"[{timestamp}] Sensor: {bool(sensor_val)} | Motor: {bool(motor_val)}")

            time_module.sleep(1)

    except KeyboardInterrupt:
        print("\nMonitoreo detenido.")
        plc.close()
        influx.close()

if __name__ == "__main__":
    main()
