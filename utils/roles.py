from rolepermissions.roles import AbstractUserRole


class Admin(AbstractUserRole):
    pass


class Buyer(AbstractUserRole):
    pass


class Vendor(AbstractUserRole):
    pass
