from .admin import Base  # keep existing minimal admin export
from .projects import Project, Property
from .users import User
from .roles import Role
from .permissions import Permission
from .mappings import user_roles, role_permissions
from .contact import Contact
from .sitevisit import SiteVisit
from .callreport import CallReport
from .task_table import Task
from .payment_received import PaymentReceived
from .due_customers import DueCustomer
from .agent import Agent
from .agent_otp import AgentOTP
from .admin_otp import AdminOTP
from .user_otp import UserOTP


__all__ = [
    "Base",
    "Project",
    "Property",
    "User",
    "Role",
    "Permission",
    "user_roles",
    "role_permissions",
    "Contact",
    "CallReport",
    "Task",
    "SiteVisit",
    "due_customer",
    "PaymentReceived",
    "Agent",
    "AgentOTP",
    "AdminOTP",
    "UserOTP",
]
