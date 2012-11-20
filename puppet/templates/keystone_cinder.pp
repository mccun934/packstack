
class {"cinder::keystone::auth":
    password => "cinder_default_password",
    public_address => "%(CONFIG_CINDER_HOST_EP)s",
    admin_address => "%(CONFIG_CINDER_HOST)s",
    internal_address => "%(CONFIG_CINDER_HOST)s",
}

