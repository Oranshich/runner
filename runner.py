import subprocess
import argparse
import psutil
import logging
import sys


def parse_arguments():
    """
    Responsible for adding and parsing the arguments.
    :return: the args that have been parsed.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("command", nargs="+",
                        help="The shell command and its arguments")
    parser.add_argument("-c", required=False, help='Number of times to '
                        'run the given command', type=int)
    parser.add_argument("--failed-count", required=False, help='Number '
                        'of allowed failed command before giving up',
                        type=int)
    parser.add_argument("--sys-trace", required=False, help='For each '
                        'failed execution, create log of system '
                        'measurements', action='store_true')
    parser.add_argument("--call-trace", required=False, help='For each '
                        'failed execution, add a log if the system calls'
                        ' ran by the command', action='store_true')
    parser.add_argument("--log-trace", required=False, help='or each '
                        'failed execution, add the command outputs '
                        'logs', action='store_true')
    parser.add_argument("--debug", required=False, help='Entering debug '
                        'mode, show each instruction executed by the '
                        'script', action='store_true')
    parser.add_argument("--net-trace", required=False, help='For each '
                        'failed execution, create a \'pcap\' file with '
                        'the network traffic during the execution',
                        action='store_true')

    args = parser.parse_known_args()

    return args


def run_command(cmd):
    """
    Responsible for running the command using the namespace
    :param cmd: the command to run
    :return: process p, the output of the command and the number of
    network packets received and sent before the command
    """
    try:
        net_count_before = psutil.net_io_counters()
        out = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               universal_newlines=True)

        p = psutil.Process()

    except KeyboardInterrupt:
        print("")

    return p, out, net_count_before


def create_log_sys_trace(out, i, net_before):
    """
    The function create a log file of all the measurements of the
    failed execution.
    :param out: the process of the command
    :param i: index of the command
    :param net_before: the number of
    network packets received and sent before the command
    :return: the log string of the sys trace argument
    """
    log_name = 'sys_trace_' + str(i) + '.log'

    cpu = out.cpu_percent()
    disk_io = out.io_counters()
    mem = out.memory_percent()
    net_after = psutil.net_io_counters()
    packet_recieve = net_after.packets_recv - net_before.packets_recv
    packet_sent = net_after.packets_sent - net_before.packets_sent

    to_log = ["disk_io: " + str(disk_io._asdict()),
              "\nmemory percentage: " + str(mem) + "%",
              "\ncpu percentage: " + str(cpu) + "%", "\nPackets recived:"
              " " + str(packet_recieve), "\nPackets recived: " +
              str(packet_recieve), "\nPackets sent: " + str(packet_sent)]

    return to_log, log_name


def create_log_call_trace(cmd, i):
    """
    Creates a log of all system calls made by the command.
    :param cmd: the command.
    :param i: index of the command.
    :return: new command with the strace command for getting all the
    system calls.
    """
    string_command = " ".join(cmd)
    new_command = "_".join(cmd)
    log_name = 'call_' + new_command + '_' + str(i) + '.log '
    new_command = 'strace -f -o ' + log_name + string_command

    return new_command.split(), log_name


def create_log_trace(stdout, stderr, index):
    """
    Creating a log file contains stdout and stderr output.
    :param stdout: stdout output.
    :param stderr: stderr output.
    :param index: index of the command.
    """
    to_log = str(stdout) + "\n" + stderr
    log_name = "log_trace_run_" + str(index) + ".log"
    save_to_log(to_log, log_name)


def save_to_log(to_log, log_name):
    """
    Creates a log file and write the content to it.
    :param to_log: the content of the log file.
    :param log_name: the name of the log file.
    :return:
    """
    file = open(log_name, "a")
    file.writelines(to_log)


def delete_call_log(call_log_name):
    """
    Deletes the system calls log.
    :param call_log_name: name of the log file to delete
    """
    cmd = 'rm ' + call_log_name
    out = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE,
                           universal_newlines=True)

    out.communicate()


def run_script():
    """
    The main function, responsible for managing the arguments and to
    runs the command.
    :return: the most frequent return code
    """
    args, unknown = parse_arguments()
    cmd = args.command
    cmd.extend(unknown)
    number_of_failed_executions = 0
    number_of_success_executions = 0

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    number_of_times = 1
    if args.c:
        number_of_times = args.c
    try:
        logging.debug("Start the execution")
        for i in range(number_of_times):
            command, call_log_name = create_log_call_trace(cmd, i)
            logging.debug("Running the " + str(i+1) + " command")
            logging.debug("Running " + str(" ".join(cmd)))
            p, out, net_before = run_command(command)
            to_log, sys_log_name = create_log_sys_trace(p, i, net_before)
            stdout, stderr = out.communicate()

            logging.debug("Execution return code: " + str(out.returncode))
            if out.returncode == 1:
                number_of_failed_executions += 1
                if args.sys_trace:
                    logging.debug("Saving sys trace log")
                    save_to_log(to_log, sys_log_name)
                if not args.call_trace:
                    delete_call_log(call_log_name)
                else:
                    logging.debug("Saving call trace log")
                if args.log_trace:
                    logging.debug("Saving call trace log")
                    create_log_trace(stdout, stderr, i)
                if args.failed_count:
                    args.failed_count -= 1
                    if args.failed_count == 0:
                        break
            else:
                number_of_success_executions += 1
                delete_call_log(call_log_name)
            logging.debug("Finishing Execution " + str(i+1))
    except KeyboardInterrupt:
        print("")

    print("Number of executions failed: ", number_of_failed_executions)
    print("Number of executions succeeded: ", number_of_success_executions)

    if number_of_failed_executions > number_of_success_executions:
        return 1

    return 0


if __name__ == '__main__':
    run_script()
