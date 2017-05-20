import os
import glob
import logging
import papis.utils

COMMANDS = [
    "add",
    "check",
    "config",
    "edit",
    "export",
    "list",
    "rm",
    "mv",
    "open",
    "browse",
    "test",
    "update",
    "run",
    "sync"
]

logger = logging.getLogger("commands")

def init_internal_commands(parser):
    global COMMANDS
    global logger
    commands = dict()
    cmd = None
    logger.debug("Initializing commands")
    for command in COMMANDS:
        logger.debug(command)
        exec("from .%s import %s" % (command, command.capitalize()))
        cmd = eval(command.capitalize())(parser)
        cmd.setParser(parser)
        cmd.init()
        commands[command] = cmd
    return commands

def init_external_commands(parser):
    from .external import External
    commands = dict()
    paths = []
    paths.append(papis.config.get_scripts_folder())
    paths += os.environ["PATH"].split(":")
    for path in paths:
        scripts = glob.glob(os.path.join(path, "papis-*"))
        if len(scripts):
            for script in scripts:
                cmd = External(parser)
                cmd.init(script)
                commands[cmd.get_command_name()] = cmd
    return commands


def init(parser):
    commands = dict()
    commands.update(init_internal_commands(parser))
    commands.update(init_external_commands(parser))
    return commands


class Command(object):

    args = None
    subparser = None

    def __init__(self, parser=None):
        self.parser = parser
        self.logger = logging.getLogger(self.__class__.__name__)

    def init(self):
        pass

    def setParser(self, parser):
        """TODO: Docstring for setParser.

        :parser: TODO
        :returns: TODO

        """
        self.parser = parser

    def getParser(self):
        """TODO: Docstring for getParser.
        :returns: TODO

        """
        return self.parser

    def pick(self, options, papis_config, pick_config={}):
        """TODO: Docstring for pick.

        :options: TODO
        :returns: TODO

        """
        import os
        import sys
        if not pick_config:
            pick_config = dict(
                header_filter=lambda x: "{:<70.70}|{:<20.20} ({:.4})".format(
                    x["title"] or x.getMainFolderName(),
                    x["author"] or "*" * 20,
                    str(x["year"] or "****")
                ),
                match_filter=lambda x:
                    os.path.dirname(
                        x.getMainFolder()
                    ).replace(
                        os.environ["HOME"], ""
                    ).replace(
                        "/", " "
                    ) +
                    (x["title"] or "") +
                    (x["author"] or "") +
                    (str(x["year"]) or "****")
            )
        return papis.utils.pick(
            options,
            papis_config,
            pick_config
        )

    def main(self, config=None, args=None):
        if not args:
            self.args = args
