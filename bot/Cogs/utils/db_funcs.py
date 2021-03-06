import sqlite3
import json
from os import getcwd


conn = sqlite3.connect('discord_bot.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()


def create_tables():
    c.execute("""CREATE TABLE IF NOT EXISTS infractions (
        id integer,
        active integer,
        guild_id integer,
        user_id integer,
        admin integer,
        type text,
        expires text,
        reason text
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS server_specific (
        guild_id integer,
        prefix text,
        mute_role_id integer,
        voice_mute_role_id integer,
        admin_role_ids text,
        moderator_role_ids text
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS user_specific (
        user_id integer,
        polls integer,
        total_poll_votes integer,
        commands integer,
        xp integer,
        level integer
    )""")


def guild_init(guild_id):
    c.execute("""INSERT INTO server_specific(guild_id, prefix, mute_role_id, voice_mute_role_id, admin_role_ids, moderator_role_ids) 
                VALUES (:g_id, :prefix, :m_role, :vm_role, :a_roles, :mod_roles)""", 
                {
                    'g_id': guild_id,
                    'prefix': '++',
                    'm_role': 0,
                    'vm_role': 0,
                    'a_roles': '0',
                    'mod_roles': '0'
                })
    conn.commit()
    with open(f'{getcwd()}\\bot\\guild_log.json', 'r+') as guild_log:
        guilds_inits = json.load(guild_log)
        guilds_inits.append(guild_id)
        guild_log.seek(0)
        guild_log.write(json.dumps(guilds_inits))
        guild_log.truncate()
    print(f'Constructed necessary elements for guild {guild_id} in database')


def get_expired_infractions():
    '''Grabs all active expired from the database'''
    c.execute("""SELECT * 
                FROM infractions 
                WHERE active=1 AND (expires < datetime('now'))
                """)
    found = c.fetchall()
    return [dict(infraction) for infraction in found]


def grab_active_user_infractions(user_id):
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

def update_in_guild(guild_id, column, updated_value):
    c.execute(f"""UPDATE server_specific
                SET {column}=:new_val""",
                {
                    'new_val': updated_value
                })
    conn.commit()