import pygame, sys

class Player:

    # *--STATS--*
    #level is the player's level, while exp is what the player gains to increase in level
    #dollars is the money the player gains throughout runs while s_coin (soul coins) is the metacurrency
    def __init__(self, Name, HP, ATK, CRIT_DMG, CRIT_CHANCE, LEVEL, EXP, DOLLARS, S_COIN):
        self.Name = Name
        self.HP = HP
        self.ATK = ATK
        self.CRIT_DMG = CRIT_DMG
        self.CRIT_CHANCE = CRIT_CHANCE
        self.LEVEL = LEVEL
        self.EXP = EXP 
        self.DOLLARS = DOLLARS
        self.S_COIN = S_COIN


    #dev only, dont keep in final
    def show_stat(self):
        print(f"""
Name: {self.Name}
HP: {self.HP}
ATK: {self.ATK}
CRIT_DMG: {self.CRIT_DMG}
CRIT_CHANCE: {self.CRIT_CHANCE}
LEVEL: {self.LEVEL}
EXP: {self.EXP}
DOLLARS: {self.DOLLARS}
S_COIN: {self.S_COIN}""")


    
    