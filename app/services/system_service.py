import os
import subprocess
import psutil

class sytemService:
    @staticmethod
    def get_syst_stats():
        try:
            # Usiamo il comando vcgencmd che è il modo ufficiale di Raspberry/Dietpi
            # se vcgencmd non è installato, torniamo al metodo del file
            output = subprocess.check_output(["vcgencmd", "measure_temp"]).decode("utf8")
            # L'poutput è tipo : temp=45.2'C
            cpu_temp = float(output.replace("temp=", "").replace("'C\n", ""))

        except:
            try:
                with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
                    cpu_temp = round(float(f.read())/ 1000, 1)
            except:
                cpu_temp = "N/A"
        
        return {
            "cpu_temp": cpu_temp,
            "cpu_usage": psutil.cpu_percent(interval=None),
            "ram_usage": psutil.virtual_memory().percent,
            "status": "Online",
            "uptime": "dietpi Active"
        }