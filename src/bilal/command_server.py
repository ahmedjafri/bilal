from importlib import resources
import signal
from typing import List
from bottle import template, request, static_file, timedelta
from threading import Lock, Thread
from bilal.praytimes import PrayTimes
from bilal.azan_config import AzanConfigLoader
from bilal.azan_loader import AzanLoader
from bilal.azan_scheduler import AzanScheduler
from bilal.azan_player import AzanPlayer
from bilal.azan_loader import Azan
from logging import Logger
import os
from bottle import response, Bottle
from json import dumps
from datetime import datetime, time

app = Bottle()


def kill_process():
    """Simulates post-processing logic"""
    time.sleep(1)  # Simulate long task
    pid = os.getpid()  # Get the current process ID
    os.kill(pid, signal.SIGTERM)
    print("Killing process to reload fresh state")


class CommandServer:
    logger: Logger
    azan_player: AzanPlayer
    azan_scheduler: AzanScheduler
    azan_loader: AzanLoader
    config_loader: AzanConfigLoader
    playing_azan: Lock = Lock()

    def __init__(
        self,
        logger: Logger,
        azan_player: AzanPlayer,
        azan_scheduler: AzanScheduler,
        azan_loader: AzanLoader,
        config_loader: AzanConfigLoader,
    ):
        self.logger = logger
        self.azan_player = azan_player
        self.azan_scheduler = azan_scheduler
        self.azan_loader = azan_loader
        self.config_loader = config_loader
        self.app = Bottle()
        self.app.get("/config")(self.get_config)
        self.app.post("/config")(self.update_config)

        self.app.route("/command/<command>")(self.command)
        self.app.get("/metadata")(self.metadata)
        self.app.route("/<filename>")(self.web)
        self.app.route("/")(self.web)

    def runBottle(self):
        self.app.run(host="0.0.0.0", port=8080)

    def playAzanAsync(self, azan_file):
        if self.playing_azan.locked():
            return

        self.playing_azan.acquire()
        self.azan_player.play_azan(True, azan_file)
        self.playing_azan.release()

    def metadata(self):
        next_azan: Azan = self.azan_loader.get_next_azan()

        # Check if a date parameter was provided
        date_param = request.query.get("date")
        target_date = datetime.now()

        if date_param:
            try:
                # Parse the date from the query parameter (format: YYYY-MM-DD)
                target_date = datetime.strptime(date_param, "%Y-%m-%d")
            except ValueError:
                # If date parsing fails, use current date
                pass
        elif target_date.day != next_azan.azan_time.day:
            target_date = target_date + timedelta(days=1)

        day_azans: List[Azan] = self.azan_loader.get_azans_for_day(target_date)

        rv = {
            "upcoming_azan": next_azan.to_dict(),
            "azans_for_day": [azan.to_dict() for azan in day_azans],
            "available_azans": self.azan_player.list_azan_filenames(),
            "quiet_hours_start": self.config_loader.getConfig().quiet_times_start,
            "quiet_hours_end": self.config_loader.getConfig().quiet_times_end,
            "azan_methods": PrayTimes().methods,
        }

        if os.path.exists("azan_clock_log_file.log"):
            lines: list[str]
            with open("azan_clock_log_file.log", "r") as file:
                lines = file.readlines()

            # Extract the last 200 lines (or less if there are fewer lines in the file)
            last_lines = lines[-100:]

            # Join the lines to create a single string
            latest_log = "".join(last_lines)

            # Assign the latest log to rv["latest_log"]
            rv["latest_log"] = latest_log

        response.content_type = "application/json"
        return dumps(rv)

    def command(self, command):
        self.logger.info(
            f"Command called. cmd={command} params={request.params.__dict__}"
        )
        if command == "play_azan":
            self.logger.info("Playing azan from server")
            azan_file = request.GET.get(
                "file", self.azan_player.list_azan_filenames()[0]
            )
            thread = Thread(target=self.playAzanAsync, args=([azan_file]))
            thread.start()
        elif command == "stop_azan":
            self.logger.info("Stopping azan from server")
            self.azan_player.stop_azan()
        else:
            response.content_type = "application/json"
            response.status = 400
            return dumps({"error": "no command found"})

        return template("<b>Run {{command}}", command=command)

    def web(self, filename="index.html"):
        file_path = resources.files("bilal").joinpath("www", filename)
        print(file_path)
        return static_file(filename, root=os.path.dirname(file_path))

    def get_config(self):
        """Retrieve the current configuration."""
        response.content_type = "application/json"
        config = self.config_loader.getConfig()
        return dumps(config.__dict__, indent=2)

    def update_config(self):
        """Update the configuration and restart components."""
        try:
            new_config_data = request.json
            if not new_config_data:
                response.status = 400
                return {"error": "Invalid JSON data"}

            # Load existing config
            current_config = self.config_loader.getConfig()

            # Update config values if provided
            for key, value in new_config_data.items():
                if hasattr(current_config, key):
                    setattr(current_config, key, value)

            # Save updated config
            self.config_loader.setConfig(current_config)

            # Stop scheduler
            self.azan_scheduler.stop()

            # Update scheduler with new loader
            self.azan_scheduler.update_loader(self.azan_loader)

            # Restart scheduling
            self.azan_scheduler.schedule_next_azan()

            return {"message": "Configuration updated successfully"}

        except Exception as e:
            response.status = 500
            return {"error": str(e)}
