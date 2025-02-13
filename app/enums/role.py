from .basicEnum import BasicEnum

class RoleType(BasicEnum):
    
    Admin = 'Admin'
    Superuser = 'Superuser'
    Vendor = 'Vendor'
    InventoryManager = 'InventoryManager'