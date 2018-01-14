""" Module for running stuff
"""
import time
import threading

class Runner:
    """ Runner object
    """
    def __init__(self, name: str):
        self.next_call = 0
        self.name = name

    def process(self):
        """ override for process, return number of seconds for next call
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

class Processor(threading.Thread):
    """ Background thrad to get data for display
    """

    def __init__(self, verbose: bool = False):
        super(Processor, self).__init__()
        self.stopped = False
        self.processors = []
        self.verbose = verbose
        self.loop_count = 0
        self.lock = threading.Lock()

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

    def run(self):
        """ run the processors, thread override
        """
        for processor in self.processors:
            processor.setup()

        now = time.time()
        min_next_call = now+1000
        sleep_sec = 1
        while not self.stopped:
            for processor in self.processors:
                if processor.next_call <= now:
                    delay = processor.process()
                    processor.next_call = now + delay
                    if processor.next_call < min_next_call:
                        min_next_call = processor.next_call
                    self.__log_msg__("ran ", processor.name, "and next call is",
                                     time.asctime(time.localtime(min_next_call)))
            with self.lock:
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
