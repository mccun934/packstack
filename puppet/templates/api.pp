
class {'apache':}

class {'apache::mod::proxy_http':}

# We need to turn this off so that appache can open some of the ports
# that are needed, I couldn't see a boolean that allows me to do this
exec{'setenforce 0':
  path => '/usr/sbin',
  notify => Class['apache']
}
