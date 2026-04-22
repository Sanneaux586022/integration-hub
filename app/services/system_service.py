import logging
import subprocess

import psutil

# Questo logger prenderà il nome del file (es. app.services.system)
logger = logging.getLogger(__name__)


class systemService:
    @staticmethod
    def get_syst_stats():
        cpu_temp = "N/A"

        try:
            # Fallback: lettura diretta dal kernel
            with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
                cpu_temp = round(float(f.read()) / 1000, 1)
        except (FileNotFoundError, PermissionError, ValueError) as e_fallback:
            # Qui è un ERROR perché abbiamo finito le opzioni
            logger.error(f"Fallimento totale lettura temperatura: {e_fallback}")
            cpu_temp = "N/A"

        return {
            "cpu_temp": cpu_temp,
            "cpu_usage": psutil.cpu_percent(interval=None),
            "ram_usage": psutil.virtual_memory().percent,
            "status": "Online",
        }
