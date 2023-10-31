import pyblish.api
import subprocess
import re
import os


class CollectLicenceData(pyblish.api.InstancePlugin):
    """Collect Licence Data"""

    hosts = ["nuke"]
    label = "Collect Licence Data"
    order = pyblish.api.CollectorOrder + 0.4990

    def process(self, instance):
        """
        """
        # Define the command to run
        # TODO: avoid hardcoded path
        command = f'/prod/softprod/tools/linux/rlmutil rlmstat -c {os.environ["foundry_LICENSE"]} -avail'

        # Define the pattern for matching the number of available licenses for nuke_i
        pattern = r'nuke_i v\d+\.\d+ available: (\d+)'

        # Run the command and capture the output
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, text=True)

        # Use regex to find the match in the output
        match = re.search(pattern, result.stdout)

        # Check if a match is found
        if match:
            # Extract the number of available licenses
            available_licenses = int(match.group(1))
            print(f"Available licenses for nuke_i: {available_licenses}")
        else:
            print("No match found for nuke_i licenses.")
            return False

        if available_licenses == 0:
            return False

