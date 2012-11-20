class { 'swift::keystone::auth':
  address  => '%(CONFIG_SWIFT_PROXY_EP)s',
  password => 'swift_default_password',
}
