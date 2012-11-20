"""
Installs and configures an openstack api server
"""

import logging
import os
import uuid

import engine_validators as validate
import basedefs
import common_utils as utils
from ospluginutils import NovaConfig, getManifestTemplate, appendManifestFile, PackStackError

# Controller object will be initialized from main flow
controller = None

# Plugin name
PLUGIN_NAME = "OS-API"
PLUGIN_NAME_COLORED = utils.getColoredText(PLUGIN_NAME, basedefs.BLUE)

logging.debug("plugin %s loaded", __name__)

def initConfig(controllerObject):
    global controller
    controller = controllerObject
    logging.debug("Adding Openstack api configuration")
    paramsList = [
                  {"CMD_OPTION"      : "api-host",
                   "USAGE"           : "The IP address of the server on which to place api endpoints, this must be different from all other hosts configured",
                   "PROMPT"          : "The IP address of the server on which to place api endpoints, this must be different from all other hosts configured",
                   "OPTION_LIST"     : [],
                   "VALIDATION_FUNC" : validate.validatePing,
                   "DEFAULT_VALUE"   : "127.0.0.1",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_API_HOST",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                 ]

    groupDict = { "GROUP_NAME"            : "OSAPI",
                  "DESCRIPTION"           : "OpenStack API endpoints paramaters",
                  "PRE_CONDITION"         : "CONFIG_API_INSTALL",
                  "PRE_CONDITION_MATCH"   : "y",
                  "POST_CONDITION"        : False,
                  "POST_CONDITION_MATCH"  : True}

    controller.addGroup(groupDict, paramsList)


def initSequences(controller):
    if controller.CONF['CONFIG_API_INSTALL'] != 'y':
        return

    # If we are installing a API server then is should be different to all other hosts
    # This enforces us to have a single user facing server and also
    # makes it easier for us not to have to worry about port conflicts
    CONFIG_API_HOST = controller.CONF['CONFIG_API_HOST']
    for k,v in controller.CONF.items():
        if k == 'CONFIG_API_HOST': continue
        if not '_HOST' in k: continue

        if CONFIG_API_HOST in [host.strip() for host in v.split(',')]:
            raise PackStackError("%s contains the API server host, they must be different"%k)

    steps = [
             {'title': 'Creating OS API endpoint server Manifests', 'functions':[createmanifest]},
    ]
    controller.addSequence("Installing OpenStack API", [], [], steps)

def createmanifest():
    manifestfile = "%s_api.pp"%controller.CONF['CONFIG_API_HOST']
    manifestdata = getManifestTemplate("api.pp")

    ports = ['5000']
    manifestdata += """\napache::vhost::proxy{'keystone': port => '5000', dest => "http://%s:5000", }"""%controller.CONF['CONFIG_KEYSTONE_HOST']
    if controller.CONF['CONFIG_GLANCE_INSTALL'] == 'y':
        ports.append('9292')
        manifestdata += """\napache::vhost::proxy{'glance': port => '9292', dest => "http://%s:9292", }"""%controller.CONF['CONFIG_GLANCE_HOST']
    if controller.CONF['CONFIG_NOVA_INSTALL'] == 'y':
        ports.append('8774')
        manifestdata += """\napache::vhost::proxy{'nova-api': port => '8774', dest => "http://%s:8774", }"""%controller.CONF['CONFIG_NOVA_API_HOST']
        ports.append('8773')
        manifestdata += """\napache::vhost::proxy{'nova-ec2': port => '8773', dest => "http://%s:8773", }"""%controller.CONF['CONFIG_NOVA_API_HOST']
    if controller.CONF['CONFIG_CINDER_INSTALL'] == 'y':
        ports.append('8776')
        manifestdata += """\napache::vhost::proxy{'cinder': port => '8776', dest => "http://%s:8776", }"""%controller.CONF['CONFIG_CINDER_HOST']
    if controller.CONF['CONFIG_SWIFT_INSTALL'] == 'y':
        ports.append('8080')
        manifestdata += """\napache::vhost::proxy{'swift': port => '8080', dest => "http://%s:8080", }"""%controller.CONF['CONFIG_SWIFT_PROXY']
    if controller.CONF['CONFIG_HORIZON_INSTALL'] == 'y':
        ports.append('80')
        manifestdata += """\napache::vhost::proxy{'horizon': port => '80', dest => "http://%s:80", }"""%controller.CONF['CONFIG_HORIZON_HOST']

    manifestdata += """\nfirewall { '001 endpoints incomming': proto    => 'tcp', dport    => [%s], action   => 'accept', }"""%",".join(["'%s'"%port for port in ports])

    appendManifestFile(manifestfile, manifestdata)

