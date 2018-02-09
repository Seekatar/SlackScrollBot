""" Module for running stuff
sudo mkdir /var/slackscrollbot
sudo chmod 0777 /var/slackscrollbot
"""
import time
import threading
import logging
from logging.handlers import RotatingFileHandler

class Runner:
    """ Runner object
    """
    def __init__(self, name: str):
        self.next_call = 0
        self.name = name

    def process(self):
        """ override for process, return number of seconds for next call and boolean indicating an error
        """
        pass

    def setup(self):
        """ override for setup
        """
        pass

    def cleanup(self):
        """ override to cleanup
        """
        pass

    def hasError(self):
        """ last run has error
        """
        pass

class Processor(threading.Thread):
    """ Background thread to get data for display
    """

    def __init__(self, verbose: bool = False):
        super(Processor, self).__init__()
        self.stopped = False
        self.processors = []
        self.verbose = verbose
        self.loop_count = 0
        self.lock = threading.Lock()
        self.hasError = False

        # logging.basicConfig(filename="/var/slackscrollbot/log.txt", level=logging.WARNING)
        logger = logging.getLogger('slackscrollbot-log')
        handler = RotatingFileHandler("/var/slackscrollbot/log.txt", maxBytes=5000000, backupCount=3)
        logger.addHandler(handler)
        logger.setLevel(logging.WARNING)

    def __log_msg__(self, msg, *args):
        if self.verbose:
            print(msg, " ".join(args))

    def add_processor(self, processor: Runner):
        """ add a processor, not thread safe so call before running
        """
        self.processors.append(processor)
        return self

    def get_loop_count(self):
        """ get number of time we've looped, to see if alive
        """
        with self.lock:
            return self.loop_count

    def has_error(self):
        """ did we get an error last pass
        """
        with self.lock:
            return self.hasError

    def run(self):
        """ run the processors, thread override
        """
        for processor in self.processors:
            processor.setup()

        sleep_sec = 1
        while not self.stopped:
            now = time.time()
            errorInPass = False
            for processor in self.processors:
                if processor.next_call <= now:
                    delay = 5
                    try:
                        (delay,processorError) = processor.process()
                        if processorError:
                            errorInPass = True
                    except Exception:
                        errorInPass = True
                        logging.exception(time.asctime(time.localtime(time.time()))+\
                                        " Exception from processor "+processor.name)

                    processor.next_call = time.time() + delay
                    self.__log_msg__("ran ", processor.name, "at", time.asctime(time.localtime(now)),
                                     "and next call is at",
                                     time.asctime(time.localtime(processor.next_call)),
                                     "since delay is", str(delay))
            with self.lock:
                self.hasError = errorInPass
                self.loop_count += 1
            time.sleep(sleep_sec)

        for processor in self.processors:
            processor.cleanup()

    def stop(self):
        """ stop the thread
        """
        print("Stopping....")
        self.stopped = True
        self.join()
        print("Stopped.")
