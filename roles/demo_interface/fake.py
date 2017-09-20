import subprocess
import time
import unirest


def run_cmd(cmd):
    """Run a command in the shell"""
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    out = {}
    out['stdout'] = stdout.strip()
    out['stderr'] = stderr.strip()
    out['rc'] = process.returncode
    return out


def run_cmd_nowait(cmd):
    """Run a command without waiting"""
    proc = subprocess.Popen(cmd, shell=True,
                            stdin=None, stdout=None, stderr=None, close_fds=True)


def callback_function(response):
    return


def main():
    while True:
        run_cmd_nowait('curl 8.8.8.8 --max-time 5')
        # unirest.post("http://8.8.8.8:3030", headers={"Accept": "application/json"}, params={
        #     "parameter": 23, "id": "bar"}, callback=callback_function)
        print 'foo'
        time.sleep(1)


main()
