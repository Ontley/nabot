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
        mute_role_id integer,
        voice_mute_role_id integer,
        admin_role_ids text
    )""")

def get_active_infractions():
    '''Grabs all active infractions from the database'''
    c.execute("""SELECT * 
                        FROM infractions 
                        WHERE (expires > datetime('now')) AND (type='mute' OR type='tempban')
                        """)
    rv = dict(c.fetchone())[0]
    return rv

def get_expired_infractions():
    '''Grabs all active infractions from the database'''
    c.execute("""SELECT * 
                FROM infractions 
                WHERE active=1 AND (expires < datetime('now'))
                """)
    return dict(c.fetchone())[0]

def grab_user_infractions(user_id):
    '''Gets a user's active mute (can't be more than one) from the db'''
    c.execute("""SELECT * 
                FROM infractions 
                WHERE user_id=:user_id AND (expires > datetime('now'))""",
                {'user_id': user_id}
                )
    return dict(c.fetchone())[0]


def get_from_guild(guild_id, needed_value):
    c.execute(f"""SELECT {needed_value}
                    FROM server_specific
                    WHERE guild_id=:g_id""",
                    {
                        'g_id': guild_id
                    }
                    )
    rv = dict(c.fetchone())
    return rv[needed_value]