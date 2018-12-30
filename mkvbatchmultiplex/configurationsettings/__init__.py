
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Maintain configuration

keys have to strings

It works with basic data types:

    - bool, byes, numbers: int, float, complex, strings

and dictionaries, lists and tuples of basic data types

binary data that can converted to base64 and save as bytes
can work the conversion from byres to binary is not
manage by the class

CM0001
"""

import ast
import logging
import xml
import xml.etree.ElementTree as ET
import xml.dom.minidom as DOM

from pathlib import Path

MODULELOG = logging.getLogger(__name__)
MODULELOG.addHandler(logging.NullHandler())

class ConfigurationSettings:
    """
    Manage configuration settings

    The class is iterable returning key, value pairs
    """

    def __init__(self, log=False):

        self._config = {}
        self._current = 0
        self._len = 0
        self._log = log

    def __iter__(self):

        return self

    def __next__(self):
        if self._current >= self._len:
            self._current = 0
            raise StopIteration
        else:
            self._current += 1
            key = list(self._config)[self._current - 1]
            return [key, self._config[key]]

    def __bool__(self):

        return len(self._config)

    def __len__(self):

        return len(self._config)

    def set(self, key, value):
        """
        set configuration item the key must be a string
        value can be basic data type
        with dict, list, tuples of basic types

        :param key: configuration element
        :type key: str
        :param value: element value
        :type value: basic data type
        """

        self._config[key] = value
        self._len = len(self._config)

    def get(self, key):
        """
        get configuration item

        :param key: configuration element
        :type key: str
        :rtype: object
        """

        if key in self._config:
            return self._config[key]
        else:
            if self._log:
                s = str(key)
                MODULELOG.debug("CM0001: key not found - %s", s)

        return None

    def toXML(self, root=None, name=None):
        """
        Returns the configuration in XML format
        if root is None returns the current configuration

        :rtype: xml.etree.ElementTree.Element
        """

        if name is None:
            name = "Config"

        config = ET.Element(name)

        if root is not None:
            root.append(config)

        for key, value in self:
            configElement = ET.SubElement(config, "ConfigSetting")
            configElement.attrib = {"id": key, "type": type(value).__name__}
            configElement.text = str(value)

        if root is None:
            return config

        return root

    def fromXML(self, xmlDoc, name=None):
        """
        Restore configuration from xml

        :param xmlDoc: xml document containing configuration data
        """
        self._config = {}

        if name is None:
            searchIn = 'Config/ConfigSetting'
        else:
            searchIn = name + "/ConfigSetting"

        for setting in xmlDoc.findall(searchIn):
            key = setting.attrib["id"]

            if setting.attrib["type"] == "str":
                value = setting.text
            else:
                value = ast.literal_eval(setting.text)

            self.set(key, value)

    def xmlPrettyPrint(self, root=None):
        """
        Returns configuration xml Pretty Printed

        :rtype: xml.dom.minidom
        """

        if root is not None:
            if not isinstance(root, xml.etree.ElementTree.Element):
                return None
        else:
            root = self.toXML()

        xmlDoc = DOM.parseString(ET.tostring(root))

        xmlPretty = xmlDoc.toprettyxml(indent="    ")

        return xmlPretty

def main():
    """Testing ead and write configuration to file"""

    configFile = Path(Path.cwd(), "configmanager.xml")
    xmlFile = str(configFile)

    b = b'mkvbatchmultiplex'
    configuration = ConfigurationSettings()
    configuration.set("bool", True)
    configuration.set("base64sting", "AdnQywACAAAAAAHmAAAAoAAACM4AAAR5AAAB7wAAAMYAAAjFAAAEcAAAAAAAAAAACgA=")
    configuration.set("base86bytes", "AdnQywACAAAAAAHmAAAAoAAACM4AAAR5AAAB7wAAAMYAAAjFAAAEcAAAAAAAAAAACgA=".encode())
    configuration.set("dict", {"key1": 1, "key2": 2, 3: b})
    configuration.set("list", [2, 3, "list", {"key1": 1, 2: [2]}])
    configuration.set("int", 13)
    configuration.set("float", 1.3e200)
    configuration.set("complex", 1+3j)
    configuration.set("tuple", (1.11, 2.22, 3.33))

    print("\nConfiguration set\n")
    for key, value in configuration:
        print("Key = {0}, type = {2} value = {1}".format(key, value, type(value).__name__))

    root = ET.Element("VergaraSoft")
    xmlConfig = configuration.toXML(root)
    tree = ET.ElementTree(xmlConfig)
    tree.write(xmlFile)

    tree = ET.ElementTree(file=xmlFile)
    root = tree.getroot()
    configuration.fromXML(root)

    print("\nRead from configuration file\n")
    for key, value in configuration:
        print("Key = {0}, type = {2}, value = {1}".format(key, value, type(value).__name__))

    prettyXML = configuration.xmlPrettyPrint(root)

    print()
    print(prettyXML)

if __name__ == '__main__':
    main()
