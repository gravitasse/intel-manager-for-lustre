#
# ========================================================
# Copyright (c) 2012 Whamcloud, Inc.  All rights reserved.
# ========================================================


"""NTP actions."""

from chroma_agent import shell
from chroma_agent.plugins import ActionPlugin

import os


def unconfigure_ntp(args):
    args.node = ""
    configure_ntp(args)


def configure_ntp(args):
    from tempfile import mkstemp
    tmp_f, tmp_name = mkstemp(dir = '/etc')
    f = open('/etc/ntp.conf', 'r')
    added_server = False
    for line in f.readlines():
        if args.node == "":
            if line.startswith("server "):
                continue
            elif line.startswith("# Commented by chroma-agent: "):
                line = line[29:]
        else:
            if line.startswith("server "):
                if not added_server:
                    os.write(tmp_f, "server %s\n" % args.node)
                    added_server = True
                line = "# Commented by chroma-agent: %s" % line
        os.write(tmp_f, line)
    f.close()
    os.close(tmp_f)
    os.chmod(tmp_name, 0644)
    if not os.path.exists("/etc/ntp.conf.pre-chroma"):
        os.rename("/etc/ntp.conf", "/etc/ntp.conf.pre-chroma")
    os.rename(tmp_name, "/etc/ntp.conf")

    # make sure the time is very close before letting ntpd take over
    shell.run(['service', 'ntpd', 'stop'])
    shell.run(['service', 'ntpdate', 'restart'])
    # signal the process
    rc, stdout, stderr = shell.run(['service', 'ntpd', 'start'])


class RsyslogPlugin(ActionPlugin):
    def register_commands(self, parser):
        p = parser.add_parser("configure-ntp",
                              help="configure NTP server")
        p.add_argument("--node", required=True,
                       help="NTP server")
        p.set_defaults(func=configure_ntp)

        p = parser.add_parser("unconfigure-ntp",
                              help="unconfigure NTP server")
        p.set_defaults(func=unconfigure_ntp)
