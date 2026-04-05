import datetime
from threading import Thread, Event, Lock
from bilal.azan_player import AzanPlayer
from bilal.azan_loader import Azan, AzanLoader
from logging import Logger


class AzanScheduler:
    """
    Manages scheduling and playback of Azan (call to prayer).
    Ensures that scheduled Azan plays at the correct time and allows graceful shutdown.
    """

    def __init__(
        self, azan_player: AzanPlayer, azan_loader: AzanLoader, logger: Logger
    ):
        self.azan_player = azan_player
        self.azan_loader = azan_loader
        self.logger = logger
        self._last_scheduled_azan = None
        self.threads = []  # Track active threads
        self.shutdown_event = Event()  # Signal to stop running threads
        self.lock = Lock()  # Protect access to thread list

    def _azan_thread_function(self, azan: Azan):
        """
        Thread function to wait until the scheduled Azan time and then play it.
        The thread can be interrupted if a shutdown is requested.
        """
        time_to_azan_secs = (azan.azan_time - datetime.datetime.now()).total_seconds()

        if time_to_azan_secs > 0:
            self.logger.info(
                f"Sleeping for {time_to_azan_secs / 60:.2f} min to play Azan"
            )

        # Wait for the azan time or shutdown event, whichever comes first
        self.shutdown_event.wait(timeout=time_to_azan_secs)

        if not self.shutdown_event.is_set():
            self.logger.info("Playing Azan now.")
            self.schedule_next_azan()
            self.azan_player.play_azan()
        else:
            self.logger.info("Azan playback skipped due to shutdown.")

    def schedule_next_azan(self):
        current_datetime = datetime.datetime.now()
        next_azan = self.azan_loader.get_next_azan(current_datetime)
        self.logger.info(f"Next azan time is {next_azan.azan_time}")
        self.schedule_azan(next_azan)

    def schedule_azan(self, azan: Azan):
        """
        Schedules an Azan to play at the specified time.
        """
        self.logger.info(f"Scheduling Azan for {azan.salat} at {azan.azan_time}")
        self._last_scheduled_azan = azan

        thread = Thread(target=self._azan_thread_function, args=(azan,))
        thread.start()

        with self.lock:
            self.threads.append(thread)  # Track active threads

    def stop(self):
        """
        Signals all scheduled Azan threads to stop and waits for them to finish.
        """
        self.logger.info("Stopping AzanScheduler and waiting for threads to exit...")
        self.shutdown_event.set()  # Wake up sleeping threads

        with self.lock:
            for thread in self.threads:
                thread.join()  # Ensure threads exit cleanly
            self.threads.clear()

        self.logger.info("AzanScheduler stopped.")

    def update_loader(self, new_loader):
        """
        Update the azan loader with a new instance and reset state.

        Args:
            new_loader: New AzanLoader instance to use for calculations
        """
        with self.lock:
            self.azan_loader = new_loader
            self.shutdown_event.clear()  # Reset shutdown flag
            self.logger.info("Updated Azan loader with new configuration")
