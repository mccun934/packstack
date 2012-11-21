
class {"nova::keystone::auth":
    password    => "nova_default_password",
    public_address => "%(CONFIG_NOVA_API_HOST_EP)s",
    admin_address => "%(CONFIG_NOVA_API_HOST)s",
    internal_address => "%(CONFIG_NOVA_API_HOST)s",
    public_protocol => "%(CONFIG_PUBLIC_PROTO)s",
    cinder => "true",
}

