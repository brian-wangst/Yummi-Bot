import sqlite3

def initialize_database():
    conn = sqlite3.connect('League.db')
    cursor = conn.cursor()

    # Create Champion_Codes table if not exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Champion_Codes (
            id TEXT PRIMARY KEY,
            champion_name TEXT NOT NULL,
            champion_abillities TEXT NOT NULL
        )
    ''')

    # Create Items table if not exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Items (
            id TEXT PRIMARY KEY,
            Item_Name TEXT NOT NULL,
            Local_Ref TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Runes (
            id TEXT PRIMARY KEY,
            Rune_Name TEXT NOT NULL,
            Local_Ref TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Summoners (
            id TEXT PRIMARY KEY,
            Summoner_Name TEXT NOT NULL,
            Local_Ref TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            Discord_id TEXT PRIMARY KEY,
            Discord_name TEXTNOT NULL,
            Game_name TEXT NOT NULL,
            Tag_line TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()

# Initialize the database
initialize_database()