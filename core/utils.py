from datetime import timedelta


def moment(t: timedelta):
    return {
        "days": t.days,
        "hours": t.seconds // 3600,
        "minutes": (t.seconds // 60) % 60,
    }


def moment_text(t: timedelta):
    mt = moment(t)
    text = ""
    if mt["days"] and mt["days"] != 0:
        text += f'{mt["days"]} day'
        if mt["days"] > 1:
            text += "s "
        else:
            text += " "
    if mt["hours"] and mt["hours"] != 0:
        text += f'{mt["hours"]} hour'
        if mt["hours"] > 1:
            text += "s "
        else:
            text += " "
    if mt["minutes"] and mt["minutes"] != 0:
        text += f'{mt["minutes"]} minute'
        if mt["minutes"] > 1:
            text += "s "
        else:
            text += " "

    return text
