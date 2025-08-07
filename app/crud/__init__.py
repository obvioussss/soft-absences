# Import des fonctions CRUD pour maintenir la compatibilité avec l'ancien code
from .users import (
    get_user,
    get_user_by_email,
    get_users,
    create_user,
    update_user,
    delete_user
)

from .absences import (
    get_absence_request,
    get_absence_requests,
    create_absence_request,
    create_admin_absence,
    update_absence_request,
    update_absence_request_status,
    delete_absence_request,
    get_calendar_events
)

from .calculations import (
    calculate_business_days,
    calculate_used_leave_days,
    get_dashboard_data,
    get_user_absence_summary
)

from .sickness import (
    get_sickness_declaration,
    get_sickness_declarations,
    create_sickness_declaration,
    update_sickness_declaration_file,
    mark_sickness_declaration_email_sent,
    mark_sickness_declaration_viewed
)

# Export toutes les fonctions pour maintenir la compatibilité
__all__ = [
    # Users
    'get_user',
    'get_user_by_email', 
    'get_users',
    'create_user',
    'update_user',
    'delete_user',
    
    # Absences
    'get_absence_request',
    'get_absence_requests',
    'create_absence_request',
    'create_admin_absence',
    'update_absence_request',
    'update_absence_request_status',
    'delete_absence_request',
    'get_calendar_events',
    
    # Calculations
    'calculate_business_days',
    'calculate_used_leave_days',
    'get_dashboard_data',
    'get_user_absence_summary',
    
    # Sickness
    'get_sickness_declaration',
    'get_sickness_declarations',
    'create_sickness_declaration',
    'update_sickness_declaration_file',
    'mark_sickness_declaration_email_sent',
    'mark_sickness_declaration_viewed'
] 