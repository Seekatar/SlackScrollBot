""" Module for running stuff
sudo mkdir /var/slackscrollbot
sudo chmod 0777 /var/slackscrollbot
"""
import time
import threading
import logging

class Runner:
    """ Runner object
    """
    def __init__(self, name: str):
        self.next_call = 0
        self.name = name
        self.has_error = False

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
        return self.has_error

    def setError(self, error: bool):
        """ sets the last run error
        """
        self.has_error = error

class Processor(threading.Thread):
    """ Background thread to get data for display
    """

    def __init__(self, verbose: bool = False):
        super(Processor, self).__init__()
        self.stopped = False
        self.runners = []
        self.verbose = verbose
        self.loop_count = 0
        self.lock = threading.Lock()
        self.hasError = False

        logging.info("Processor starting up")

    def __log_msg__(self, msg, *args):
        if self.verbose:
            print(msg, " ".join(args))

    def add_runner(self, runner: Runner):
        """ add a runner, not thread safe so call before running
        """
        self.runners.append(runner)
        logging.info("Processor added %s", runner.name)
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
        """ run the runners, thread override
        """
        for runner in self.runners:
            logging.info("About to setup %s",runner.name)
            runner.setup()

        logging.info("Processor running....")

        sleep_sec = 1
        while not self.stopped:
            now = time.time()
            errorInPass = False
            for runner in self.runners:
                if runner.next_call <= now:
                    delay = 5
                    try:
                        (delay,processorError) = runner.process()
                        runner.setError(processorError)
                        if processorError:
                            logging.warning("Processor %s returned error on loop %d", runner.name, self.loop_count)
                        else:
                            logging.debug("Processor %s returned ok error on loop %d", runner.name, self.loop_count)
                    except Exception:
                        runner.setError(True)
                        logging.exception("Exception from runner %s on loop %d", runner.name, self.loop_count)

                    runner.next_call = time.time() + delay
                    self.__log_msg__("ran ", runner.name, "at", time.asctime(time.localtime(now)),
                                     "and next call is at",
                                     time.asctime(time.localtime(runner.next_call)),
                                     "since delay is", str(delay))
                errorInPass = errorInPass or runner.has_error

            hadError = self.hasError
            with self.lock:
                self.hasError = errorInPass
                self.loop_count += 1
            if hadError and not self.hasError:
                logging.info('Recovered from previous errors.')
            time.sleep(sleep_sec)

        for runner in self.runners:
            runner.cleanup()

    def stop(self):
        """ stop the thread
        """
        print("Stopping....")
        self.stopped = True
        self.join()
        print("Stopped.")
