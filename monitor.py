import subprocess
import threading
import time
import sys

class ScriptMonitor:
    def __init__(self, script_path, text_file, interval, *script_args):
        self.script_path = script_path
        self.text_file = text_file
        self.interval = int(interval)  # Convert interval to integer
        self.script_args = script_args
        self.named_args = self.parse_named_args(script_args)
        self.positional_args = [arg for arg in script_args if not self.is_named_arg(arg)]
        self.stop_event = threading.Event()
        self.dstat_process = None
        self.dstat_thread = threading.Thread(target=self.run_dstat)

    def parse_named_args(self, args):
        """Parse named arguments from the list of arguments, including --key=value and --key-k=value."""
        named_args = {}
        for arg in args:
            if '=' in arg and (arg.startswith('--') or '-' in arg[2:]):
                key, value = arg.lstrip('-').split('=', 1)
                named_args[key] = value
        return named_args

    def is_named_arg(self, arg):
        """Check if an argument is a named argument."""
        return '=' in arg and (arg.startswith('--') or '-' in arg[2:])

    def run_dstat(self):
        """Runs `dstat -c -m` at the specified interval and saves the output to a text file."""
        with open(self.text_file, mode='w') as file:
            self.dstat_process = subprocess.Popen(
                ['dstat', '-c', '--mem-adv'],
                stdout=file,
                stderr=subprocess.PIPE,
                text=True
            )
            while not self.stop_event.is_set():
                time.sleep(self.interval)

            # Terminate dstat process once the user script has finished
            if self.dstat_process:
                self.dstat_process.terminate()
                try:
                    self.dstat_process.wait(timeout=self.interval)  # Give dstat time to terminate
                except subprocess.TimeoutExpired:
                    self.dstat_process.kill()  # Force kill if not terminated
                    self.dstat_process.wait()  # Ensure termination

    def run_script(self):
        """Executes the user's script based on its type."""
        if self.script_path.endswith('.py'):
            self.run_python_script()
        elif self.script_path.endswith('.sh'):
            self.run_bash_script()
        else:
            print(f"Unsupported script type: {self.script_path}", file=sys.stderr)
            sys.exit(1)

    def run_python_script(self):
        """Executes a Python script with named arguments."""
        try:
            # Prepare the command with named arguments
            command = ['python', self.script_path] + self.positional_args
            for key, value in self.named_args.items():
                command.append(f'--{key}={value}')

            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
            self.script_error(e)

    def run_bash_script(self):
        """Executes a Bash script."""
        try:
            subprocess.run(['bash', self.script_path] + self.positional_args, check=True)
        except subprocess.CalledProcessError as e:
            self.script_error(e)

    def script_error(self, error):
        """Handles errors during script execution."""
        print(f"Error executing user script: {error}", file=sys.stderr)

    def start(self):
        """Starts the monitoring and execution."""
        self.dstat_thread.start()
        self.run_script()
        time.sleep(self.interval)
        self.stop_event.set()
        self.dstat_thread.join()

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python monitor.py <interval> <output_file> <script_path> [<arg1> <arg2> ... <argN>]")
        sys.exit(1)

    interval = sys.argv[1]
    text_file = sys.argv[2]
    script_path = sys.argv[3]
    script_args = sys.argv[4:]

    monitor = ScriptMonitor(script_path, text_file, interval, *script_args)
    monitor.start()
