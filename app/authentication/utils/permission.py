from rest_framework import exceptions
def check_permission(user_id_one, user_id_two):
    if  user_id_one != user_id_two:
        raise exceptions.PermissionDenied("You do not have permission to access!")
    return None
