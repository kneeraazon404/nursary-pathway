def get_pclaim(user):
    """
    Method to get user info and blacklist it to logout user
    """
    try:
        claim = user.password[-10:]
        bclaim = claim.encode("utf-8")
        pclaim = str(int.from_bytes(bclaim, "big"))
        return pclaim
    except Exception as e:
        print(e)
        return None


def get_name(user):
    if user.first_name and user.last_name:
        f_name = user.first_name + " " + user.last_name
    elif user.first_name and not user.last_name:
        f_name = user.first_name
    elif not user.first_name and not user.last_name:
        f_name = user.profile.company_name
    else:
        f_name = user.username

    return f_name
