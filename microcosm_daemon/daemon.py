"""
Base class for command-line driven asynchronous worker.

"""
from abc import ABCMeta, abstractmethod, abstractproperty
from argparse import ArgumentParser

from microcosm.api import create_object_graph
from microcosm.loaders import load_each, load_from_environ, load_from_dict

from microcosm_daemon.api import StateMachine
from microcosm_daemon.runner import ProcessRunner, SimpleRunner


class Daemon(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        self.parser = None
        self.args = None
        self.graph = None

    @abstractproperty
    def name(self):
        """
        Define the name of this process (and its object graph).

        Must be overridden in a subclass.

        """
        pass

    @property
    def components(self):
        """
        Define the required object graph components.

        Most subclasses will override to inject additional components.

        """
        return [
            "logger",
            "logging",
            "error_policy",
            "signal_handler",
            "sleep_policy",
        ]

    @property
    def defaults(self):
        return {}

    @property
    def loader(self):
        """
        Define the object graph config loader.

        """
        return load_each(
            load_from_dict(self.defaults),
            load_from_environ,
        )

    @property
    def import_name(self):
        """
        Define the object graph import name, if any.

        """
        return None

    @property
    def root_path(self):
        """
        Define the object graph root path, if any.

        """
        return None

    @abstractmethod
    def __call__(self, graph):
        """
        Define the graph's initial callable state.

        """
        pass

    def run(self):
        """
        Run the daemon.

        """
        parser = self.make_arg_parser()
        args = parser.parse_args()

        if args.processes < 1:
            parser.error("--processes must be positive")
        elif args.processes == 1:
            runner = SimpleRunner(self)
        else:
            runner = ProcessRunner(args.processes, self)

        runner.run()

    def start(self):
        """
        Start the state machine.

        """
        # reprocess the arguments because some aspects of argparse are not pickleable
        # and will fail under multiprocessing
        self.parser = self.make_arg_parser()
        self.args = self.parser.parse_args()

        self.graph = self.create_object_graph(self.args)
        self.graph.logger.info("Starting daemon {}".format(self.name))
        self.run_state_machine()

    def run_state_machine(self):
        state_machine = StateMachine(self.graph, self)
        state_machine.run()

    def make_arg_parser(self):
        """
        Create the argument parser.

        """
        parser = ArgumentParser()

        flags = parser.add_mutually_exclusive_group()
        flags.add_argument("--debug", action="store_true")
        flags.add_argument("--testing", action="store_true")

        parser.add_argument("--processes", type=int, default=1)
        return parser

    def create_object_graph(self, args):
        """
        Create (and lock) the object graph.

        """
        graph = create_object_graph(
            name=self.name,
            debug=args.debug,
            testing=args.testing,
            import_name=self.import_name,
            root_path=self.root_path,
            loader=self.loader,
        )
        self.create_object_graph_components(graph)
        graph.lock()
        return graph

    def create_object_graph_components(self, graph):
        graph.use(*self.components)
