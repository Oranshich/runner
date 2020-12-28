import runner
import sys
import glob
import logging
import pytest
import pdb


def test_run_command_with_no_args():
    return_code = runner.run_script()
    assert return_code == 1


def test_run_only_one_command():
    sys.argv = ['runner.py', 'ls']
    return_code = runner.run_script()
    assert return_code == 0


def test_prints_only_one_command(capsys):
    sys.argv = ['runner.py', 'ls']
    runner.run_script()
    out, err = capsys.readouterr()
    assert out == "Number of executions failed:  0\nNumber of executions succeeded:  1\n"


def test_run_command_with_argument():
    sys.argv = ['runner.py', 'ls', '-l']
    return_code = runner.run_script()
    assert return_code == 0

def test_run_command_n_times(capsys):
    sys.argv = ['runner.py', 'ls', '-l', '-c', '5']
    return_code = runner.run_script()
    assert return_code == 0
    out, err = capsys.readouterr()
    assert out == "Number of executions failed:  0\nNumber of executions succeeded:  5\n"

def test_run_with_bad_command():
    sys.argv = ['runner.py', 'jsnwn']
    return_code = runner.run_script()
    assert return_code == 1


def test_sys_trace_log_not_created():
    sys.argv = ['runner.py', 'ls', '-l', '--sys-trace']
    runner.run_script()
    assert not glob.glob('sys_trace_0.log')


def test_sys_trace_log_created():
    sys.argv = ['runner.py', 'cat', 'bla', '--sys-trace']
    runner.run_script()
    assert glob.glob('sys_trace_0.log')


def test_call_trace_not_created():
    sys.argv = ['runner.py', 'ls', '-l', '--call-trace']
    runner.run_script()
    assert not glob.glob('call_ls_-l_0.log')

def test_call_trace_created():
    sys.argv = ['runner.py', 'cat', 'bla', '--call-trace']
    runner.run_script()
    assert glob.glob('call_cat_bla_0.log')

def test_count_failed_executions(capsys):
    sys.argv = ['runner.py', 'cat', 'bla', '-c', '5', '--failed-count', '3']
    return_code = runner.run_script()
    assert return_code == 1
    out, err = capsys.readouterr()
    assert out == "Number of executions failed:  3\nNumber of executions succeeded:  0\n"

def test_log_trace_not_created():
    sys.argv = ['runner.py', 'ls', '-l', '--log-trace']
    runner.run_script()
    assert not glob.glob('log_trace_run_0.log')

def test_log_trace_created():
    sys.argv = ['runner.py', 'cat', 'bla', '--log-trace']
    runner.run_script()
    assert glob.glob('log_trace_run_0.log')


def test_debug_printing(capsys, caplog):
    caplog.set_level(logging.DEBUG)
    sys.argv = ['runner.py', 'ls', '-l', '--debug']
    runner.run_script()
    out, err = capsys.readouterr()
    assert out == "Number of executions failed:  0\n" \
        "Number of executions succeeded:  1\n" \
        and "DEBUG    root:runner.py:163 Start the execution\n" \
        "DEBUG    root:runner.py:166 Running the 1 command\n" \
        "DEBUG    root:runner.py:167 Running ls -l\n" \
        "DEBUG    root:runner.py:172 Execution return code: 0\n" \
        "DEBUG    root:runner.py:192 Finishing Execution 1\n" in caplog.text

def test_debug_printing_with_sys_trace(capsys, caplog):
    caplog.set_level(logging.DEBUG)
    sys.argv = ['runner.py', 'cat', 'bla', '--debug', '--sys-trace']
    runner.run_script()
    out, err = capsys.readouterr()
    assert out == "Number of executions failed:  1\n" \
        "Number of executions succeeded:  0\n" \
        and "DEBUG    root:runner.py:163 Start the execution\n" \
        "DEBUG    root:runner.py:166 Running the 1 command\n" \
        "DEBUG    root:runner.py:167 Running cat bla\n" \
        "DEBUG    root:runner.py:172 Execution return code: 1\n" \
        "DEBUG    root:runner.py:176 Saving sys trace log\n" \
        "DEBUG    root:runner.py:192 Finishing Execution 1\n" in caplog.text