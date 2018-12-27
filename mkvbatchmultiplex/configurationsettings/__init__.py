
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Maintain configuration

CM0001
"""

import logging
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

    log = False

    def __init__(self):

        self._config = {}
        self._current = 0
        self._len = 0

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
        set configuration item

        :param key: configuration element
        :type key: str
        :param value: element value
        :type value: object
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

        return self._config[key]

    def toXML(self):
        """
        Returns the configuration in XML format

        :rtype: xml.etree.ElementTree.Element
        """

        root = ET.Element("VergaraSoft")
        config = ET.Element("Config")
        root.append(config)

        for key, value in self:
            configElement = ET.SubElement(config, "ConfigSetting")
            configElement.attrib = {"id": key, "type": type(value).__name__}
            configElement.text = str(value)

        return root

    def fromXML(self, xml):
        """
        Restore configuration from xml

        :param xml: xml document containing configuration data
        """

        self._config = {}

        for setting in xml.findall('./Config/ConfigSetting'):
            key = setting.attrib["id"]

            if setting.attrib["type"] == "bool":
                value = bool(setting.text)
            else:
                value = setting.text

            self.set(key, value)


    def xmlPrettyPrint(self):
        """
        Returns configuration xml Pretty Printed

        :rtype: xml.dom.minidom
        """

        xml = DOM.parseString(ET.tostring(self.toXML()))

        xmlPretty = xml.toprettyxml(indent="    ")

        return xmlPretty

def main():
    """Testing ead and write configuration to file"""
    configFile = Path(Path.cwd(), "configmanager.xml")
    xmlFile = str(configFile)

    configuration = ConfigurationSettings()
    configuration.set("logging", True)
    configuration.set("geometry", "AdnQywACAAAAAAHmAAAAoAAACM4AAAR5AAAB7wAAAMYAAAjFAAAEcAAAAAAAAAAACgA=")
    configuration.set("font", "MS Shell Dlg 2,7.8,-1,5,50,0,0,0,0,0")

    for key, value in configuration:
        print("Key = {}, value = {}".format(key, value))

    print("\n\n")

    xmlConfig = configuration.toXML()
    tree = ET.ElementTree(xmlConfig)
    tree.write(xmlFile)

    tree = ET.ElementTree(file=xmlFile)
    root = tree.getroot()
    configuration.fromXML(root)

    for key, value in configuration:
        print("Key = {}, value = {}".format(key, value))

if __name__ == '__main__':
    main()
