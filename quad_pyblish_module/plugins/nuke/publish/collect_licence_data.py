import pyblish.api
import subprocess
import re
import os


class CollectLicenceData(pyblish.api.InstancePlugin):

    """Collect Licence Data"""

    hosts = ["nuke"]
    label = "Collect Licence Data"
    order = pyblish.api.CollectorOrder + 0.4990
    # TODO: avoid hardcoded path
    rlm_path = "/prod/softprod/tools/linux/rlmutil"

    def get_available_licenses(self):
        """
        """
        # Define the command to run
        avail_command = f'{self.rlm_path} rlmstat -c {os.environ["foundry_LICENSE"]} -avail'

        # Define the pattern for matching the number of available licenses for nuke_i
        pattern = r'nuke_i v\d+\.\d+ available: (\d+)'

        # Run the command and capture the output
        result = subprocess.run(avail_command, shell=True, stdout=subprocess.PIPE, text=True)

        # Use regex to find the match in the output
        match = re.search(pattern, result.stdout)

        # Check if a match is found
        if match:
            # Extract the number of available licenses
            available_licenses = int(match.group(1))
        else:
            return False

        if available_licenses == 0:
            return False

        return True

    def get_user_licenses(self):
        # Define the pattern for matching user licenses for nuke_i
        user_command = f'{self.rlm_path} rlmstat -c {os.environ["foundry_LICENSE"]} -u {os.environ["USER"]}'

        user_pattern = r'nuke_i v\d+\.\d+: (\S+)@\S+ (\d+)/(\d+)'

        # Run the command and capture the output
        result = subprocess.run(user_command, shell=True, stdout=subprocess.PIPE, text=True)

        # Use regex to find the match in the output
        matches = re.findall(user_pattern, result.stdout)

        # Check if any matches are found
        if matches:
            return True

        return False

    def process(self, instance):
        # Check if user already have a licence
        if self.get_user_licenses():
            return True

        # Check if user can get an available license
        if self.get_available_licenses():
            return True

        # User can't publish
        raise Exception("No available licence ! Can't publish")
