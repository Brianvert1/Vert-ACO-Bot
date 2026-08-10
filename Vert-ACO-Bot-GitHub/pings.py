from database import find_user_for_profile

def get_ping(profile_name):
    user_id = find_user_for_profile(profile_name)
    return f"<@{user_id}>" if user_id else ""
