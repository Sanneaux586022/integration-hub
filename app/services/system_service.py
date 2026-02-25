import logging
import subprocess
import psutil

# Questo logger prenderà il nome del file (es. app.services.system)
logger = logging.getLogger(__name__)

class sytemService:
    @staticmethod
    def get_syst_stats():
        cpu_temp = "N/A"
        
        try:
            # Tentativo primario: vcgencmd
            output = subprocess.check_output(["vcgencmd", "measure_temp"], stderr=subprocess.STDOUT).decode("utf8")
            cpu_temp = float(output.replace("temp=", "").replace("'C\n", ""))
        except Exception as e:
            # Logghiamo l'errore del primo tentativo come WARNING (non è critico perché abbiamo il fallback)
            logger.warning(f"Metodo vcgencmd fallito: {e}. Provo fallback su file di sistema...")
            
            try:
                # Fallback: lettura diretta dal kernel
                with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
                    cpu_temp = round(float(f.read()) / 1000, 1)
            except Exception as e_fallback:
                # Qui è un ERROR perché abbiamo finito le opzioni
                logger.error(f"Fallimento totale lettura temperatura: {e_fallback}")
                cpu_temp = "N/A"

        return {
            "cpu_temp": cpu_temp,
            "cpu_usage": psutil.cpu_percent(interval=None),
            "ram_usage": psutil.virtual_memory().percent,
            "status": "Online"
        }