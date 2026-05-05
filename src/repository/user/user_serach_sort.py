from orm.user.user import mstlogin, mstrole

USER_SEARCHABLE_COLUMNS = {
    "user_name": mstlogin.c.user_name,
    "role": mstrole.c.role,
}

USER_SORTABLE_COLUMNS = {
    "id": mstlogin.c.id,
    "user_name": mstlogin.c.user_name,
    "role": mstrole.c.role,
}
