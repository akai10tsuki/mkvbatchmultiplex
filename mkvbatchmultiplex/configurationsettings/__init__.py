
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Maintain configuration

CM0001
"""

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

    def toXML(self, root=None):
        """
        Returns the configuration in XML format
        if root is None returns the current configuration

        :rtype: xml.etree.ElementTree.Element
        """

        config = ET.Element("Config")

        if root is not None:
            root.append(config)

        for key, value in self:
            configElement = ET.SubElement(config, "ConfigSetting")
            configElement.attrib = {"id": key, "type": type(value).__name__}
            configElement.text = str(value)

        if root is None:
            return config

        return root

    def fromXML(self, xmlDoc):
        """
        Restore configuration from xml

        :param xmlDoc: xml document containing configuration data
        """

        self._config = {}

        for setting in xmlDoc.findall('./Config/ConfigSetting'):
            key = setting.attrib["id"]

            if setting.attrib["type"] == "bool":
                value = bool(setting.text)
            else:
                value = setting.text

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

    configuration = ConfigurationSettings()
    configuration.set("logging", True)
    configuration.set("geometry", "AdnQywACAAAAAAHmAAAAoAAACM4AAAR5AAAB7wAAAMYAAAjFAAAEcAAAAAAAAAAACgA=")
    configuration.set("font", "MS Shell Dlg 2,7.8,-1,5,50,0,0,0,0,0")

    for key, value in configuration:
        print("Key = {}, value = {}".format(key, value))

    print("\n\n")

    root = ET.Element("VergaraSoft")
    xmlConfig = configuration.toXML(root)
    tree = ET.ElementTree(xmlConfig)
    tree.write(xmlFile)

    tree = ET.ElementTree(file=xmlFile)
    root = tree.getroot()
    configuration.fromXML(root)

    for key, value in configuration:
        print("Key = {}, value = {}".format(key, value))

    prettyXML = configuration.xmlPrettyPrint()

    print(prettyXML)

if __name__ == '__main__':
    main()
