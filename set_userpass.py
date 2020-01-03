#!/usr/bin/env python3
import sys
import time
from loguru import logger
from netmiko.paloalto.paloalto_panos import PaloAltoPanosBase

# GLOBAL VARS
LOG_LEVEL = "INFO"
SSH_PEM = sys.argv[1]
ADMIN_USER = sys.argv[2]
USER_TO_CHANGE = sys.argv[3]
PASSWORD = sys.argv[4]
MGMT_IP = sys.argv[5]

# Logging Settings
logger.remove()
logger.add(sys.stderr, level=LOG_LEVEL)


def main():
    if len(sys.argv) < 6:
        logger.error("You are missing a required parameter, please try again")
        sys.exit(2)

    session = PaloAltoPanosBase(ip=MGMT_IP,
                                username=ADMIN_USER,
                                key_file=SSH_PEM)

    logger.debug(f'session information: {session}')

    config_commands = [
        'set cli scripting-mode on',
        session.config_mode(),
        f'set mgt-config users {USER_TO_CHANGE} permissions role-based superuser yes',
        f'set mgt-config users {USER_TO_CHANGE} password'
    ]

    config_mode = False

    for cmd in config_commands:
        logger.info(cmd)
        output = session.send_command_timing(cmd)
        logger.debug(output)
        if "Enter password" in output:
            output += session.send_command_timing(PASSWORD,
                                                  strip_prompt=False,
                                                  strip_command=False)
            if "Confirm password" in output:
                output += session.send_command_timing(PASSWORD,
                                                      strip_prompt=False,
                                                      strip_command=False)
                logger.debug(output)

    logger.info("committing changes...\n")
    logger.debug(session.commit())
    logger.info("exiting commit mode...\n")
    logger.debug(session.exit_config_mode())
    logger.info("exiting SSH session\n")
    logger.debug(session.cleanup())


if __name__ == "__main__":
    main()
