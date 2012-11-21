
class {"glance::keystone::auth":
    password => "glance_default_password",
    public_address => "%(CONFIG_GLANCE_HOST_EP)s",
    admin_address => "%(CONFIG_GLANCE_HOST)s",
    internal_address => "%(CONFIG_GLANCE_HOST)s",
    public_protocol => "%(CONFIG_PUBLIC_PROTO)s",
}

