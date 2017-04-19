#!/usr/bin/env python
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright (C) 2010 - 2011 Red Hat, Inc.
# Copyright (C) 2015 Tobias Mueller <muelli@cryptobitch.de>
#

import dbus

# This example asks settings service for all configured connections.
# It also asks for secrets, demonstrating the mechanism the secrets can
# be handled with.

bus = dbus.SystemBus()

def merge_secrets(proxy, config, setting_name):
    try:
        # returns a dict of dicts mapping name::setting, where setting is a dict
        # mapping key::value.  Each member of the 'setting' dict is a secret
        secrets = proxy.GetSecrets(setting_name)

        # Copy the secrets into our connection config
        for setting in secrets:
            for key in secrets[setting]:
                config[setting_name][key] = secrets[setting][key]
    except Exception as e:
        pass

def dict_to_string(d, indent):
    # Try to trivially translate a dictionary's elements into nice string
    # formatting.
    dstr = ""
    for key in d:
        val = d[key]
        str_val = ""
        add_string = True
        if type(val) == type(dbus.Array([])):
            for elt in val:
                if type(elt) == type(dbus.Byte(1)):
                    str_val += "%s " % int(elt)
                elif type(elt) == type(dbus.String("")):
                    str_val += "%s" % elt
        elif type(val) == type(dbus.Dictionary({})):
            dstr += dict_to_string(val, indent + "    ")
            add_string = False
        else:
            str_val = val
        if add_string:
            dstr += "%s%s: %s\n" % (indent, key, str_val)
    return dstr

def connection_to_string(config):
    # dump a connection configuration to a the console
    for setting_name in config:
        print("        Setting: %s" % setting_name)
        print(dict_to_string(config[setting_name], "            "))
    print("")


def list_connections():
    # Ask the settings service for the list of connections it provides
    service_name = "org.freedesktop.NetworkManager"
    proxy = bus.get_object(service_name, "/org/freedesktop/NetworkManager/Settings")
    settings = dbus.Interface(proxy, "org.freedesktop.NetworkManager.Settings")
    connection_paths = settings.ListConnections()

    ret = []
    # List each connection's name, UUID, and type
    for path in connection_paths:
        ret.append(Connection(path))

    return ret


class Connection(object):
    def __init__(self, dbus_connection_path,
                 service_name="org.freedesktop.NetworkManager"):
        con_proxy = bus.get_object(service_name, dbus_connection_path)
        settings_connection = dbus.Interface(con_proxy,
                                             "org.freedesktop.NetworkManager.Settings.Connection")
        config = settings_connection.GetSettings(byte_arrays=True)

        # Now get secrets too; we grab the secrets for each type of connection
        # (since there isn't a "get all secrets" call because most of the time
        # you only need 'wifi' secrets or '802.1x' secrets, not everything) and
        # merge that into the configuration data
        merge_secrets(settings_connection, config, '802-11-wireless')
        merge_secrets(settings_connection, config, '802-11-wireless-security')
        merge_secrets(settings_connection, config, '802-1x')
        merge_secrets(settings_connection, config, 'gsm')
        merge_secrets(settings_connection, config, 'cdma')
        merge_secrets(settings_connection, config, 'ppp')

        self._security = config.get('802-11-wireless-security', {})

        self._config = config

    def __str__(self):
        for setting_name in self._config:
            print("        Setting: %s" % setting_name)
            print(dict_to_string(self._config[setting_name], "            "))
        print("")

    def get_id(self):
        return self._config['connection']['id']

    def get_key(self):
        if self.get_sec_type() == 'WEP':
            return self._security.get('wep-key0')
        return self._security.get('psk')

    def get_passphrase(self):
        """Like get_key, but encoded if necessary"""
        #if self.get_sec_type() == 'WEP':
            # FIXME: digest encoding, see create_barcode_string.py
        return self.get_key()

    def get_ssid(self):
        return self._config['802-11-wireless']['ssid'].decode('utf-8')

    def get_sec_type(self):
        if 'wep-key0' in self._security:
            return 'WEP'
        return 'WPA'


list_connections()


