import sys
import subprocess
import argparse

local_arguments = ['-c', '--failed-count', '--sys-trace', '--call-trace',
                   '--log-trace', '--debug', '--help', '--net-trace']


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", nargs="+", help="The shell command and his "
                                                   "arguments")
    parser.add_argument("-c", required=False, help='Number of times to run the'
                                                   ' given command', type=int)
    parser.add_argument("--failed-count", required=False, help='Number of '
                                                               'allowed failed command before giving up', type=int)
    parser.add_argument("--sys-trace", required=False, help='For each failed '
                                                            'execution, create log of system measurements')
    parser.add_argument("--call-trace", required=False, help='For each failed '
                                                             'execution, add a log if the system calls ran by the '
                                                             'command')
    parser.add_argument("--log-trace", required=False, help='or each failed '
                                                            'execution, add the command outputs logs')
    parser.add_argument("--debug", required=False, help='Entering debug mode,'
                                                        'show each instruction executed by the script')
    parser.add_argument("--net-trace", required=False, help='For each failed '
                                                            'execution, create a \'pcap\' file with the network'
                                                            ' traffic during the execution')
    args = parser.parse_known_args()

    # parser.add_argument('-c', type=int, help='NUMBER of times to run')
    return args


def run_command(cmd, failed_count=None):
    print("cmd", cmd)
    try:
        out = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
        while True:
            nextline = out.stdout.readline()
            if nextline == '' and out.poll() is not None:
                break
            sys.stdout.write(str(nextline) + "\n")
            sys.stdout.flush()
        stdout, stderr = out.communicate()
        print("stdout: ", stdout)
        if out.returncode != 0:
            print("errorrrr: ", stderr)
    except KeyboardInterrupt:
        stdout, stderr = out.communicate()
    return out


def create_log_sys_trace(pid):
    pass


def run_script():
    args, unknown = parse_arguments()
    cmd = args.command
    cmd.extend(unknown)
    cmd = " ".join(cmd)

    if args.c:
        for i in range(args.c):
            out = run_command(cmd, args.failed_count)
            print("pid", out.pid)
            
            if out.returncode != 0:
                if args.sys_trace:
                    create_log_sys_trace(out.pid)
                if args.failed_count:
                    args.failed_count -= 1
                    if args.failed_count == 0:
                        break
    out = run_command(cmd, args.failed_count)


if __name__ == '__main__':
    run_script()
