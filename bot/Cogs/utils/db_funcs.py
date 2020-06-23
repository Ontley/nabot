import sqlite3


conn = sqlite3.connect('discord_bot.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()


def create_tables():
    c.execute("""CREATE TABLE IF NOT EXISTS infractions (
        _id integer,
        active integer,
        guild_id integer,
        user_id integer,
        type text,
        expires text,
        reason text
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS server_specific (
        guild_id integer,
        prefix text,
        mute_role integer,
        voice_mute_role integer,
        admin_roles text
    )""")

def get_active_infractions():
    '''Grabs all active infractions from the database'''
    return c.execute("""SELECT * 
                        FROM infractions 
                        WHERE (expires > datetime('now')) AND (type='mute' OR type='tempban')
                        """).fetchall()

def get_expired_infractions():
    '''Grabs all active infractions from the database'''
    return c.execute("""SELECT * 
                        FROM infractions 
                        WHERE active=1 AND (expires < datetime('now'))
                        """).fetchall()

def grab_user_infractions(user_id):
    '''Gets a user's active mute (can't be more than one) from the db'''
    return c.execute("""SELECT * 
                        FROM infractions 
                        WHERE user_id=:user_id AND (expires > datetime('now'))""",
                        {'user_id': user_id}
                        ).fetchone()


def find_mute_role(guild_id):
    '''Find the guild's mute role'''
    return c.execute("""SELECT mute_role
                        FROM server_specific
                        WHERE guild_id=:g_id""",
                        {'g_id': guild_id}
                        ).fetchone()['mute_role']

def get_from_guild(guild_id, needed_value):
    print(needed_value)
    return c.execute(f"""SELECT :needed
                        FROM server_specific
                        WHERE guild_id=:g_id""",
                        {
                            'needed': needed_value,
                            'g_id': guild_id
                        }
                        ).fetchone()
