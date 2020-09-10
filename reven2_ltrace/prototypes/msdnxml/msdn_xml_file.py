"""Parse msdn.xml to retrieve function prototypes
"""

import xml.etree.ElementTree as ET
from sys import stderr


class MsdnXmlFile(object):
    def __init__(self, msdn_path):
        try:
            self._msdn_tree = ET.parse(msdn_path)
        except Exception as e:
            print(
                "Error loading msdn db {}: {}".format(msdn_path, e),
                file=stderr,
            )
            self._msdn_tree = None

    def function_proto_str(self, symbol_name):
        function_key = "./fcts/fct/[name='{}']".format(symbol_name)
        try:
            function_node = self._msdn_tree.getroot().find(function_key)
            proto_str = function_node.find("proto").text
            if "//" in proto_str:
                # malformed prototype in msdn.xml
                return None
            return proto_str
        except Exception:
            return None
