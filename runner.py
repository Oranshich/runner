import sys
import subprocess
import argparse
import psutil
import logging

local_arguments = ['-c', '--failed-count', '--sys-trace', '--call-trace',
                   '--log-trace', '--debug', '--help', '--net-trace']


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", nargs="+", help="The shell command and its "
                                                   "arguments")
    parser.add_argument("-c", required=False, help='Number of times to run the'
                                                   ' given command', type=int)
    parser.add_argument("--failed-count", required=False, help='Number of '
                                                               'allowed failed command before giving up', type=int)
    parser.add_argument("--sys-trace", required=False, help='For each failed '
                                                            'execution, create log of system measurements', action='store_true')
    parser.add_argument("--call-trace", required=False, help='For each failed '
                                                             'execution, add a log if the system calls ran by the '
                                                             'command', action='store_true')
    parser.add_argument("--log-trace", required=False, help='or each failed '
                                                            'execution, add the command outputs logs', action='store_true')
    parser.add_argument("--debug", required=False, help='Entering debug mode,'
                                                        'show each instruction executed by the script', action='store_true')
    parser.add_argument("--net-trace", required=False, help='For each failed '
                                                            'execution, create a \'pcap\' file with the network'
                                                            ' traffic during the execution', action='store_true')
    args = parser.parse_known_args()

    # parser.add_argument('-c', type=int, help='NUMBER of times to run')
    return args


def run_command(cmd):

    try:
        print("cmd", cmd)
        print("cmd type ", type(cmd))
        net_count_before = psutil.net_io_counters()
        out = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, universal_newlines=True)

        print("return code", out.returncode)
        p = psutil.Process()
        print(p)


    except KeyboardInterrupt:
        print("")
    return p, out, net_count_before


def create_log_sys_trace(out, i, net_count_before):
    print("out return code: ", out.status())
    log_name = 'sys_trace_' +str(out.pid) + "_" +str(i) +'.log'

    cpu = out.cpu_percent()
    disk_io = out.io_counters()
    mem = out.memory_percent()
    net_count_after = psutil.net_io_counters()
    packet_recieve = net_count_after.packets_recv - net_count_before.packets_recv
    packet_sent = net_count_after.packets_sent - net_count_before.packets_sent

    to_log = ["disk_io: " + str(disk_io._asdict()),"\nmemory percentage: " + str(mem) + "%", "\ncpu percentage: "
                     + str(cpu) + "%", "\nPackets recived: " + str(packet_recieve), "\nPackets recived: "
                     + str(packet_recieve), "\nPackets sent: " + str(packet_sent)]
    print('finish sys-trace')

    return to_log, log_name


def create_log_call_trace(cmd, i):
    string_command = " ".join(cmd)
    new_command = "_".join(cmd)
    log_name = 'call_' + new_command + '_' + str(i) +'.log '
    new_command = 'strace -f -o '+ log_name + string_command
    print("new command ", new_command)
    return new_command.split(), log_name


def create_log_trace(stdout, stderr, index):
    to_log = str(stdout) + "\n" + stderr
    log_name = "log_trace_run_" + str(index) + ".log"
    save_to_log(to_log, log_name)


def save_to_log(to_log, log_name):
    file = open(log_name, "a")
    file.writelines(to_log)


def delete_call_log(call_log_name):
    cmd = 'rm ' + call_log_name
    out = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, universal_newlines=True)

    out.communicate()

def run_script():
    args, unknown = parse_arguments()
    cmd = args.command
    cmd.extend(unknown)

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    number_of_times = 1

    if args.c:
        number_of_times = args.c
    try:
        logging.debug("Start the execution")
        for i in range(number_of_times):
            command, call_log_name = create_log_call_trace(cmd, i)
            logging.debug("Running the " + str(i+1) +" command")
            logging.debug("Running " + str(" ".join(cmd)))
            p, out, net_count_before = run_command(command)
            to_log, sys_log_name = create_log_sys_trace(p, i, net_count_before)
            stdout, stderr = out.communicate()

            logging.debug("Execution return code: " + str(out.returncode))
            print("return code", out.returncode)
            if out.returncode == 1:
                if args.sys_trace:
                    logging.debug("Saving sys trace log")
                    save_to_log(to_log, sys_log_name)
                if not args.call_trace:
                    logging.debug("Saving call trace log")
                    delete_call_log(call_log_name)
                if args.log_trace:
                    logging.debug("Saving call trace log")
                    create_log_trace(stdout, stderr, i)
                if args.failed_count:
                    args.failed_count -= 1
                    if args.failed_count == 0:
                        break
            else:
                delete_call_log(call_log_name)
            logging.debug("Finishing Execution " + str(i+1))
    except KeyboardInterrupt:
        print("")


if __name__ == '__main__':
    run_script()
