import asyncio
import subprocess
import socket
import platform
import traceback
import signal
from logging import Logger
from threading import Thread, Event
from zeroconf import ServiceInfo, Zeroconf
import zeroconf

class LocalDiscovery:
    """
    Manages Zeroconf (mDNS) service registration for local discovery.
    Ensures clean shutdown when the program terminates.
    """

    def __init__(self, logger: Logger):
        self.logger = logger
        self.zeroconf = Zeroconf()
        self.shutdown_event = Event()
        self.thread = Thread(target=self._register_zeroconf)
        self.service_info = None

    def start(self):
        """Starts the Zeroconf service registration in a separate thread."""
        self.thread.start()

    def _register_zeroconf(self):
        """Registers the service with Zeroconf and handles retries."""
        net_if = "wlan0" if platform.system() != "Darwin" else "en0"
        cmd = f"/sbin/ifconfig {net_if} | grep -i mask | awk '{{print $2}}' | cut -f2 -d :"
        ip = subprocess.getoutput(cmd).strip()

        if not ip:
            self.logger.error("Failed to determine local IP address.")
            return

        self.logger.info(f"Local IP: {ip}")

        self.service_info = ServiceInfo(
            "_http._tcp.local.",
            "Bilal._http._tcp.local.",
            addresses=[socket.inet_aton(ip)],
            port=8080,
            server="bilal.local.",
        )

        for attempt in range(5):
            if self.shutdown_event.is_set():
                self.logger.info("Shutdown requested, stopping registration...")
                return

            try:
                self.logger.info(f"Registering service on bilal.local ({ip}), attempt {attempt + 1}...")
                self.zeroconf.register_service(info=self.service_info, allow_name_change=True)
                self.logger.info(f"Registered.")
                break  # Success, exit loop
            except Exception as e:
                self.logger.error(f"Failed to register service: {traceback.format_exc()}")
                if attempt < 4:
                    self.logger.info("Retrying in 60 seconds...")
                    self.shutdown_event.wait(60)  # Wait with an option to exit
                else:
                    self.logger.error("Max retries reached, giving up.")

    def stop(self):
        """Unregisters the service and stops the thread."""
        self.logger.info("Stopping Zeroconf service...")
        self.shutdown_event.set()  # Signal the thread to stop
        if self.service_info:
            asyncio.run(self.zeroconf.async_unregister_service(self.service_info))
        self.zeroconf.close()
        self.thread.join()  # Ensure thread exits
        self.logger.info("Zeroconf service stopped.")
