# navigation/helpers.py

import hashlib


class Utils:
    @staticmethod
    def generate_md5_hash(*args):
        """
        Generate an MD5 hash from the given arguments.
        :param args: Any number of stringable arguments (numbers, strings, etc.)
        :return: MD5 hash as a string.
        """
        hash_input = ''.join(map(str, args))  # Convert all args to string and concatenate
        return hashlib.md5(hash_input.encode()).hexdigest()

    @staticmethod
    def another_utility_method(param1, param2):
        # Add another utility method if needed
        return param1 + param2
