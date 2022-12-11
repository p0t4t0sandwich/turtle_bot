#!/bin/python3
#--------------------------------------------------------------------
# Project: Bot Function Library
# Purpose: Simplify creation of Discord bots.
# Author: Dylan Sperrer (p0t4t0sandwich|ThePotatoKing)
# Date: 10AUGUST2021
# Updated: 3AUGUST2022 - p0t4t0sandwich
#   - Added the linking database logic to be shared between bots.
#--------------------------------------------------------------------

# green -> 0x65bf65
# yellow -> 0xe6d132
# red -> 0xbf0f0f

# Function for simple logging
def bot_logger(path, bot, string):
    import logging
    """
    Purpose:
        Logs the String with a time and date into bot.log.
    Pre-Conditions:
        :param string: The text to send to the log file
        :param bot: The name of the bot using the log function.
        :param path: Filepath of where to save the log file.
    Post-Conditions:
        Saves all necessary data to the log file.
    Return:
        None
    """

    FORMAT = "[%(asctime)s]: [%(name)s] %(message)s"
    DATEFMT = "%d/%m/%Y %H:%M:%S"

    logging.basicConfig(
        filename=path + bot + ".log",
        encoding='utf-8',
        level=logging.DEBUG,
        format=FORMAT,
        datefmt=DATEFMT
    )

    console = logging.StreamHandler()
    console.setLevel(logging.INFO)

    # Set a format which is simpler for console use
    formatter = logging.Formatter(fmt=FORMAT, datefmt=DATEFMT)

    # Tell the handler to use this format
    console.setFormatter(formatter)

    # Add the handler to the root logger
    logging.getLogger().addHandler(console)

    logger = logging.getLogger(bot)
    logger.info(string)


def get_twitch_id(twitch_name):
    import requests
    import json
    import os
    """
    Purpose:
        Uses the Twitch API to collect a user id from a username.
    Pre-Conditions:
        :param twitch_name: The username of the Twitch user to collect the id of.
    Post-Conditions:
        None
    Return:
        The Twitch user id of the specified user.
    """
    client_id = os.getenv("TWITCH_CLIENT_ID")
    
    token_response = requests.post(
        'https://id.twitch.tv/oauth2/token',
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            },
        data = {
            'client_id': client_id,
            'client_secret': os.getenv("TWITCH_CLIENT_SECRET"),
            'grant_type': 'client_credentials'
        }
    )

    twitch_id_response = requests.get(
        'https://api.twitch.tv/helix/users',
        headers = {
            'Authorization': 'Bearer ' + json.loads(token_response.content)["access_token"],
            'Client-Id': client_id,
            },
        params=(('login', twitch_name),)
        )

    return json.loads(twitch_id_response.content)["data"][0]["id"]


# Function for linking different media accounts to the database.
def link_account(from_platform, from_platform_username, from_platform_id, to_platform, to_platform_username):
    import mysql.connector
    from mysql.connector import errorcode
    import os
    """
    Purpose:
        To link user accounts within the database.
    Pre-Conditions:
        :param from_platform: The platform the user is linking from.
        :param from_platform_username: The "from" platform username of the user.
        :param from_platform_id: The "from" platform username id of the user.
        :param to_platform: The platform the user is linking to.
        :param to_platform_username: The "to" platform username of the user.
    Post-Conditions:
        Link the specified user data within the database
    Return:
        A message notifying the user of their success/failure.
    """
    # Help response
    if to_platform == "help":
        return 'Available platforms: minecraft, discord, twitch.\n!link platform platform_username\nADDITIONAL NOTE FOR BEDROCK USERS:\nPlease ensure you include a period "." before your playername!', 100
    
    config = {
            'user': os.getenv("MYSQL_USER"),
            'password': os.getenv("MYSQL_PASSWORD"),
            'host': os.getenv("MYSQL_HOST"),
            'database': os.getenv("MYSQL_DATABASE"),
            'raise_on_warnings': True
        }

    # Simple injection sterilization
    from_platform = from_platform.replace("--","").replace("/*","").replace("%00","").replace("%16","")
    from_platform_username = from_platform_username.replace("--","").replace("/*","").replace("%00","").replace("%16","")
    from_platform_id = str(from_platform_id)
    to_platform = to_platform.replace("--","").replace("/*","").replace("%00","").replace("%16","")
    to_platform_username = to_platform_username.replace("--","").replace("/*","").replace("%00","").replace("%16","")

    err_msg = f"""
            There doesn't seem to be a MC username linked with your account, @{from_platform_username}.
            Please login to our MC server (!ip) if you haven't already, and then
            use: "!link minecraft [username]".
            Use "!link help" for details on usage.
            ADDITIONAL NOTE FOR BEDROCK USERS:
            Please ensure you include a period "." before your playername!
            """

    account_data = {
        "from_platform": from_platform,
        "from_platform_username": from_platform_username,
        "from_platform_id": from_platform_id,
        "to_platform": to_platform,
        "to_platform_username": to_platform_username
    }

    try:
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()

        if to_platform == "minecraft":
            mc_id_query = "SELECT player_id FROM player_data WHERE player_name = %(to_platform_username)s"

            # Check to see if minecraft account is in system and prevent re-assignment of minecraft accounts
            anti_yoink_query = "SELECT " + from_platform + " FROM linked_accounts WHERE player_id = (SELECT player_id FROM player_data WHERE player_name = %(to_platform_username)s) LIMIT 1"
            cursor.execute(anti_yoink_query, account_data)
            data = cursor.fetchall()
            if data != [(None,)] and data != []:
                cursor.close()
                cnx.close()
                return f"This Minecraft username is already linked to a {from_platform} account, if you think this is an error please contact an admin.", 100
        else:
            mc_id_query = "SELECT player_id FROM linked_accounts WHERE " + from_platform + " = %(from_platform_username)s"
            
            # Query to prevent account sharing (possible rewards exploit)
            anti_share_query = "SELECT * FROM linked_accounts WHERE " + to_platform + " = %(to_platform_username)s LIMIT 1"
            cursor.execute(anti_share_query, account_data)
            data = cursor.fetchall()
            if data != []:
                cursor.close()
                cnx.close()
                return "This username is already in the system, if you think this is an error please contact an admin.", 100

        cursor.execute(mc_id_query, account_data)

        data = cursor.fetchall()
        if data != []:
            account_data["player_id"] = str(data[0][0])
        else:
            cursor.close()
            cnx.close()
            return err_msg, 400

        # Creates new entry if player not referenced in linked_accounts, otherwise updates entry.
        init_row_query = (
                "INSERT INTO linked_accounts (player_id)"
                "SELECT (" + account_data["player_id"] + ")"
                "FROM DUAL WHERE NOT EXISTS (SELECT * FROM linked_accounts "
                "WHERE player_id = " + account_data["player_id"] + " LIMIT 1)"
                )
        cursor.execute(init_row_query, account_data)
        cnx.commit()

        if to_platform != "minecraft":
            # Link TO platform account
            link_account_query = (
                "UPDATE linked_accounts SET " + to_platform + " = %(to_platform_username)s WHERE player_id = " + account_data["player_id"] + ";"
            )
            cursor.execute(link_account_query, account_data)
            
            # Grab the Twitch id from the Twitch API
            if to_platform == 'twitch':
                twitch_id = get_twitch_id(to_platform_username)
                link_account_id_query = (
                    "UPDATE linked_accounts SET " + to_platform + "_id = " + twitch_id + " WHERE player_id = " + account_data["player_id"] + ";"
                )
                cursor.execute(link_account_id_query, account_data)

            cnx.commit()

        # Gather FROM user info
        if from_platform in ['discord', 'twitch']:
            platform_username_query = (
                "UPDATE linked_accounts SET " + from_platform + " = %(from_platform_username)s WHERE player_id = " + account_data["player_id"] + ";"
            )
            platform_id_query = (
                "UPDATE linked_accounts SET " + from_platform + "_id = " + from_platform_id + " WHERE player_id = " + account_data["player_id"] + ";"
            )
            cursor.execute(platform_username_query, account_data)
            cursor.execute(platform_id_query, account_data)
            cnx.commit()

        # Reward players for linking accounts
        if to_platform != "minecraft":
            reward_check_query = "SELECT redeemed_" + to_platform + " FROM currency WHERE player_id = " + account_data["player_id"] + ";"
            cursor.execute(reward_check_query)
            data = cursor.fetchall()
            if data == [(None,)]:
                link_reward_query = "UPDATE currency SET tokens = tokens + 1 WHERE player_id = " + account_data["player_id"] + ";"
                link_redeemed_query = "UPDATE currency SET redeemed_" + to_platform + " = 1 WHERE player_id = " + account_data["player_id"] + ";"
                cursor.execute(link_reward_query)
                cursor.execute(link_redeemed_query)
                cnx.commit()
        else:
            reward_check_query = "SELECT redeemed_" + from_platform + " FROM currency WHERE player_id = " + account_data["player_id"] + ";"
            cursor.execute(reward_check_query)
            data = cursor.fetchall()
            if data == [(None,)]:
                link_reward_query = "UPDATE currency SET tokens = tokens + 1 WHERE player_id = " + account_data["player_id"] + ";"
                link_redeemed_query = "UPDATE currency SET redeemed_" + from_platform + " = 1 WHERE player_id = " + account_data["player_id"] + ";"
                cursor.execute(link_reward_query)
                cursor.execute(link_redeemed_query)
                cnx.commit()

        cursor.close()
        cnx.close()

        return f"You have successfully linked your {to_platform} account!", 200

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
        cursor.close()
        cnx.close()
        return err_msg, 400
    else:
        cnx.close()

# Function for linking different media accounts to the database.
def bal(from_platform, from_platform_username):
    import mysql.connector
    from mysql.connector import errorcode
    import os
    """
    Purpose:
        To retrieve and return balance data for the specified user.
    Pre-Conditions:
        :param from_platform: The platform the user is linking from.
        :param from_platform_username: The "from" platform username of the user.
    Post-Conditions:
        Gather data from the database.
    Return:
        A message with the requested information or an error message.
    """

    config = {
            'user': os.getenv("MYSQL_USER"),
            'password': os.getenv("MYSQL_PASSWORD"),
            'host': os.getenv("MYSQL_HOST"),
            'database': os.getenv("MYSQL_DATABASE"),
            'raise_on_warnings': True
        }

    # Simple injection sterilization
    from_platform = from_platform.replace("--","").replace("/*","").replace("%00","").replace("%16","")
    from_platform_username = from_platform_username.replace("--","").replace("/*","").replace("%00","").replace("%16","")

    err_msg = f"""
            There doesn't seem to be a MC username linked with your account, @{from_platform_username}.
            Please login to our MC server (!ip) if you haven't already, and then
            use: "!link minecraft [username]".
            ADDITIONAL NOTE FOR BEDROCK USERS:
            Please ensure you include a period "." before your playername!
            """

    account_data = {
        "from_platform": from_platform,
        "from_platform_username": from_platform_username
    }

    try:
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()

        mc_id_query = "SELECT player_id FROM linked_accounts WHERE " + from_platform + " = %(from_platform_username)s"
        cursor.execute(mc_id_query, account_data)
        data = cursor.fetchall()
        if data != []:
            account_data["player_id"] = str(data[0][0])
        else:
            cursor.close()
            cnx.close()
            return err_msg, 400

        reward_check_query = "SELECT * FROM currency WHERE player_id = " + account_data["player_id"] + ";"
        cursor.execute(reward_check_query)
        data = cursor.fetchall()

        cursor.close()
        cnx.close()

        return "Tokens: " + str(data[0][2]) + "\nChannel Point Tokens: " + str(data[0][5]) + "\nExploit Tokens: " + str(data[0][3]) + "\nDonator Tokens: " + str(data[0][4]), 200

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
        cursor.close()
        cnx.close()
        return err_msg, 400
    else:
        cnx.close()

def playtime(from_platform, from_platform_username):
    import mysql.connector
    from mysql.connector import errorcode
    import os
    """
    Purpose:
        To retrieve and return playtime data for the specified user.
    Pre-Conditions:
        :param from_platform: The platform the user is linking from.
        :param from_platform_username: The "from" platform username of the user.
    Post-Conditions:
        Gather data from the database.
    Return:
        A message with the requested information or an error message.
    """

    config = {
            'user': os.getenv("MYSQL_USER"),
            'password': os.getenv("MYSQL_PASSWORD"),
            'host': os.getenv("MYSQL_HOST"),
            'database': os.getenv("MYSQL_DATABASE"),
            'raise_on_warnings': True
        }

    # Simple injection sterilization
    from_platform = from_platform.replace("--","").replace("/*","").replace("%00","").replace("%16","")
    from_platform_username = from_platform_username.replace("--","").replace("/*","").replace("%00","").replace("%16","")

    err_msg = f"""
            There doesn't seem to be a MC username linked with your account, @{from_platform_username}.
            Please login to our MC server (!ip) if you haven't already, and then
            use: "!link minecraft [username]".
            ADDITIONAL NOTE FOR BEDROCK USERS:
            Please ensure you include a period "." before your playername!
            """

    account_data = {
        "database": os.getenv("MYSQL_DATABASE"),
        "from_platform": from_platform,
        "from_platform_username": from_platform_username
    }

    try:
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()

        mc_id_query = "SELECT player_id FROM linked_accounts WHERE " + from_platform + " = %(from_platform_username)s"
        cursor.execute(mc_id_query, account_data)
        data = cursor.fetchall()
        if data != []:
            account_data["player_id"] = str(data[0][0])
        else:
            cursor.close()
            cnx.close()
            return err_msg, 400

        playtime_query = "SELECT * FROM playtime WHERE player_id = " + account_data["player_id"]

        cursor.execute(playtime_query)
        data = cursor.fetchall()[0][2:]
        
        column_names_query = """
            SELECT column_name from information_schema.columns
            WHERE table_schema = %(database)s
            AND table_name = 'playtime'
            ORDER BY ordinal_position
        """
        cursor.execute(column_names_query, account_data)
        columns = cursor.fetchall()
        columns.remove(("playtime_id",))
        columns.remove(("player_id",))

        msg = f"Total Playtime: {sum(data)} min\n"

        for i in range(len(columns)):
            if data[i] != 0:
                msg += f"{columns[i][0]}: {data[i]} min\n"

        cursor.close()
        cnx.close()

        return msg, 200

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
        cursor.close()
        cnx.close()
        return err_msg, 400
    else:
        cnx.close()