def get_username(user):
    return user.first_name or user.last_name or user.username or '-' if user else '-'
