"""
Installs and configures nova
"""

import logging
import os

import engine_validators as validate
import common_utils as utils
from ospluginutils import NovaConfig, getManifestTemplate, appendManifestFile, setEndpoint

# Controller object will be initialized from main flow
controller = None

PLUGIN_NAME = "OS-NOVA"

logging.debug("plugin %s loaded", __name__)

def initConfig(controllerObject):
    global controller
    controller = controllerObject

    paramsList = [
                  {"CMD_OPTION"      : "novaapi-host",
                   "USAGE"           : "The IP address of the server on which to install the Nova API service",
                   "PROMPT"          : "The IP address of the server on which to install the Nova API service",
                   "OPTION_LIST"     : [],
                   "VALIDATION_FUNC" : validate.validatePing,
                   "DEFAULT_VALUE"   : "127.0.0.1",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_NOVA_API_HOST",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "novacert-host",
                   "USAGE"           : "The IP address of the server on which to install the Nova Cert service",
                   "PROMPT"          : "The IP address of the server on which to install the Nova Cert service",
                   "OPTION_LIST"     : [],
                   "VALIDATION_FUNC" : validate.validatePing,
                   "DEFAULT_VALUE"   : "127.0.0.1",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_NOVA_CERT_HOST",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "novacompute-hosts",
                   "USAGE"           : "A comma seperated list of IP addresses on which to install the Nova Compute services",
                   "PROMPT"          : "A comma seperated list of IP addresses on which to install the Nova Compute services",
                   "OPTION_LIST"     : [],
                   "VALIDATION_FUNC" : validate.validateMultiPing,
                   "DEFAULT_VALUE"   : "127.0.0.1",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_NOVA_COMPUTE_HOSTS",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "libvirt-type",
                   "USAGE"           : "The libvirt type to use, if your compute server is bare metal set to kvm, if testing on a vm set to qemu",
                   "PROMPT"          : "The libvirt type to use, if your compute server is bare metal set to kvm, if testing on a vm set to qemu",
                   "OPTION_LIST"     : ["qemu", "kvm"],
                   "VALIDATION_FUNC" : validate.validateOptions,
                   "DEFAULT_VALUE"   : __get_libvirt_type_default(),
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": False,
                   "CONF_NAME"       : "CONFIG_LIBVIRT_TYPE",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "novacompute-privif",
                   "USAGE"           : "Private interface for Flat DHCP on the Nova compute servers",
                   "PROMPT"          : "Private interface for Flat DHCP on the Nova compute servers",
                   "OPTION_LIST"     : [],
                   "VALIDATION_FUNC" : validate.validateStringNotEmpty,
                   "DEFAULT_VALUE"   : "eth1",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_NOVA_COMPUTE_PRIVIF",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "novanetwork-host",
                   "USAGE"           : "The IP address of the server on which to install the Nova Network service",
                   "PROMPT"          : "The IP address of the server on which to install the Nova Network service",
                   "OPTION_LIST"     : [],
                   "VALIDATION_FUNC" : validate.validatePing,
                   "DEFAULT_VALUE"   : "127.0.0.1",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_NOVA_NETWORK_HOST",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "novanetwork-pubif",
                   "USAGE"           : "Public interface on the Nova network server",
                   "PROMPT"          : "Public interface on the Nova network server",
                   "OPTION_LIST"     : [],
                   "VALIDATION_FUNC" : validate.validateStringNotEmpty,
                   "DEFAULT_VALUE"   : "eth0",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_NOVA_NETWORK_PUBIF",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "novanetwork-privif",
                   "USAGE"           : "Private interface for Flat DHCP on the Nova network server",
                   "PROMPT"          : "Private interface for Flat DHCP on the Nova network server",
                   "OPTION_LIST"     : [],
                   "VALIDATION_FUNC" : validate.validateStringNotEmpty,
                   "DEFAULT_VALUE"   : "eth1",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_NOVA_NETWORK_PRIVIF",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "novanetwork-fixed-range",
                   "USAGE"           : "IP Range for Flat DHCP",
                   "PROMPT"          : "IP Range for Flat DHCP",
                   "OPTION_LIST"     : ["^([\d]{1,3}\.){3}[\d]{1,3}/\d\d?$"],
                   "VALIDATION_FUNC" : validate.validateRe,
                   "DEFAULT_VALUE"   : "192.168.32.0/22",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_NOVA_NETWORK_FIXEDRANGE",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "novanetwork-floating-range",
                   "USAGE"           : "IP Range for Floating IP's",
                   "PROMPT"          : "IP Range for Floating  IP's",
                   "OPTION_LIST"     : ["^([\d]{1,3}\.){3}[\d]{1,3}/\d\d?$"],
                   "VALIDATION_FUNC" : validate.validateRe,
                   "DEFAULT_VALUE"   : "10.3.4.0/22",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_NOVA_NETWORK_FLOATRANGE",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                  {"CMD_OPTION"      : "novasched-host",
                   "USAGE"           : "The IP address of the server on which to install the Nova Scheduler service",
                   "PROMPT"          : "The IP address of the server on which to install the Nova Scheduler service",
                   "OPTION_LIST"     : [],
                   "VALIDATION_FUNC" : validate.validatePing,
                   "DEFAULT_VALUE"   : "127.0.0.1",
                   "MASK_INPUT"      : False,
                   "LOOSE_VALIDATION": True,
                   "CONF_NAME"       : "CONFIG_NOVA_SCHED_HOST",
                   "USE_DEFAULT"     : False,
                   "NEED_CONFIRM"    : False,
                   "CONDITION"       : False },
                 ]
    groupDict = { "GROUP_NAME"            : "NOVA",
                  "DESCRIPTION"           : "Nova Options",
                  "PRE_CONDITION"         : "CONFIG_NOVA_INSTALL",
                  "PRE_CONDITION_MATCH"   : "y",
                  "POST_CONDITION"        : False,
                  "POST_CONDITION_MATCH"  : True}
    controller.addGroup(groupDict, paramsList)

def initSequences(controller):
    if controller.CONF['CONFIG_NOVA_INSTALL'] != 'y':
        return

    novaapisteps = [
             {'title': 'Adding Nova API Manifest entries', 'functions':[createapimanifest]},
             {'title': 'Adding Nova Keystone Manifest entries', 'functions':[createkeystonemanifest]},
             {'title': 'Adding Nova Cert Manifest entries', 'functions':[createcertmanifest]},
             {'title': 'Adding Nova Compute Manifest entries', 'functions':[createcomputemanifest]},
             {'title': 'Adding Nova Network Manifest entries', 'functions':[createnetworkmanifest]},
             {'title': 'Adding Nova Scheduler Manifest entries', 'functions':[createschedmanifest]},
             {'title': 'Adding Nova Common Manifest entries', 'functions':[createcommonmanifest]},
    ]
    controller.addSequence("Installing Nova API", [], [], novaapisteps)

def createapimanifest():
    manifestfile = "%s_api_nova.pp"%controller.CONF['CONFIG_NOVA_API_HOST']
    manifestdata = getManifestTemplate("nova_api.pp")
    appendManifestFile(manifestfile, manifestdata)

def createkeystonemanifest():

    setEndpoint(controller.CONF, 'CONFIG_NOVA_API_HOST')

    manifestfile = "%s_keystone.pp"%controller.CONF['CONFIG_KEYSTONE_HOST']
    manifestdata = getManifestTemplate("keystone_nova.pp")
    appendManifestFile(manifestfile, manifestdata)

def createcertmanifest():
    manifestfile = "%s_nova.pp"%controller.CONF['CONFIG_NOVA_CERT_HOST']
    manifestdata = getManifestTemplate("nova_cert.pp")
    appendManifestFile(manifestfile, manifestdata)

def createcomputemanifest():
    manifestdata = getManifestTemplate("nova_compute.pp")
    for host in controller.CONF["CONFIG_NOVA_COMPUTE_HOSTS"].split(","):
        manifestfile = "%s_nova.pp"%host

        server = utils.ScriptRunner(host)
        nova_config_options = NovaConfig()

        if host != controller.CONF["CONFIG_NOVA_NETWORK_HOST"]:
            nova_config_options.addOption("flat_interface", controller.CONF['CONFIG_NOVA_COMPUTE_PRIVIF'])
            validate.r_validateIF(server, controller.CONF['CONFIG_NOVA_COMPUTE_PRIVIF'])

        # if on a vm we need to set libvirt_cpu_mode to "none"
        # see https://bugzilla.redhat.com/show_bug.cgi?id=858311
        if controller.CONF["CONFIG_LIBVIRT_TYPE"] == "qemu":
            nova_config_options.addOption("libvirt_cpu_mode", "none")

        server.execute()
        appendManifestFile(manifestfile, manifestdata + "\n" + nova_config_options.getManifestEntry())

def createnetworkmanifest():
    hostname = controller.CONF['CONFIG_NOVA_NETWORK_HOST']

    server = utils.ScriptRunner(hostname)
    validate.r_validateIF(server, controller.CONF['CONFIG_NOVA_NETWORK_PRIVIF'])
    validate.r_validateIF(server, controller.CONF['CONFIG_NOVA_NETWORK_PUBIF'])
    server.execute()

    manifestfile = "%s_nova.pp"%hostname
    manifestdata = getManifestTemplate("nova_network.pp")
    appendManifestFile(manifestfile, manifestdata)

def createschedmanifest():
    manifestfile = "%s_nova.pp"%controller.CONF['CONFIG_NOVA_SCHED_HOST']
    manifestdata = getManifestTemplate("nova_sched.pp")
    appendManifestFile(manifestfile, manifestdata)

def createcommonmanifest():
    for manifestfile in controller.CONF['CONFIG_MANIFESTFILES']:
        if manifestfile.endswith("_nova.pp"):
            data = getManifestTemplate("nova_common.pp")
            appendManifestFile(os.path.split(manifestfile)[1], data)

def __get_libvirt_type_default():
    with open('/proc/cpuinfo','r') as f:
        return ('kvm', 'qemu')['hypervisor' in f.read()]
