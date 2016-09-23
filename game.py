# Basic Python3 RPG V0.6
# Created by Sam Scott on 26-07-2016
# ToDo: Shop where you can buy items in exchange for gems/coins.
# 		Buff items. Increase player damage output for the current encounter only.
#		More random events to make the game interesting. Story mode with NPC's?
#		Maybe a pet system? Or an upgradable village? (Kind of like 'A Silent Wood' (Android game))
#		GUI.
#		Powerful types of enemies that have more HP and only appear after a certain XP threshold.

import random, time, sys, os
from tkinter import *

class Character:
	def __init__(self):
		self.name = ""
		self.health = 1
		self.health_max = 1

	def do_damage(self, enemy):
		damage = min(max(random.randint(0, self.health) - random.randint(0, enemy.health), 0), enemy.health)
		enemy.health -= damage
		if damage == 0:
			player.output("%s evades %s's attack." % (enemy.name, self.name), clear = False)
		else:
			player.output("%s hurts %s! (%s -%dHP [%d/%d])" % (self.name, enemy.name, enemy.name, damage, enemy.health, enemy.health_max), clear = False)
		return enemy.health <= 0


class Player(Character):
	def __init__(self):
		Character.__init__(self)
		self.name = ""
		self.game_over = False
		self.health = 10
		self.health_max = 10
		self.level = 1
		self.xp = 0
		self.req_xp = 500 # xp required to level up (this value can change)
		self.state = "normal"
		self.inventory = {}
		self.totals = {}
		for item in treasures:
			self.inventory[item] = 0
			self.totals[item] = 0
		self.inventory["potion of healing"] = 3
		self.enemies_killed = 0
		self.passages_explored = 0

	def set_name(self, name):
		self.name = name

	def help(self):
		self.output(help_text)

	def heal(self):
		if self.inventory["potion of healing"] > 0 and self.health < self.health_max -1:
			self.inventory["potion of healing"] -= 1
			self.health += 2
			self.output("%s drinks a potion of healing. HP increases by 2." % self.name)
		elif self.inventory["potion of healing"] > 0 and self.health < self.health_max:
			self.inventory["potion of healing"] -= 1
			self.health += 1
			self.output("%s drinks a potion of healing. HP increases by 1." % self.name)
		elif self.inventory["potion of healing"] > 0 and self.health == self.health_max:
			self.output("%s doesn't need to heal right now." % self.name)
		else:
			self.output("%s doesn't have any potions of healing!" % self.name)

	def attack(self):
		if self.state != "fight":
			self.output("%s swings at nothing." % self.name)
			self.tired()
		else:
			self.output("")
			if self.do_damage(self.enemy):
				self.output("%s slaughters %s!" % (self.name, self.enemy.name), clear = False)
				self.enemy = None
				self.enemies_killed += 1
				self.state = "normal"
				self.xp += 100
			else:
				self.enemy_attacks()

	def status(self):
		if self.state == "fight":
			self.output("State: In Combat")#
		else:
			self.output("State: Exploring")
		self.output("HP: %d/%d" % (self.health, self.health_max), clear = False)
		self.output("Level: %d" % self.level, clear = False)
		self.output("XP: %d/%d" % (self.xp, self.req_xp), clear = False)
		for item in list(self.inventory.keys()):
			self.output("%s: %d" % (item.title(), self.inventory[item]), clear = False)

	def rest(self):
		if self.state != "normal":
			self.output("%s can't rest now!" % self.name)
			self.enemy_attacks()
		else:
			if self.health < self.health_max:
				self.output("%s rests." % self.name)
				if random.randint(0, 10) > 7:
					self.enemy = Enemy(self)
					self.output("%s is rudely awakened by %s [%d/%dHP]!" % (self.name, self.enemy.name, self.enemy.health, self.enemy.health_max))
					self.state = "fight"
					self.enemy_attacks()
				else:
					self.health += 1
					self.output("%s feels better now. HP increases by 1." % self.name)
			else:
				self.output("%s doesn't feel tired right now." % self.name)

	def flee(self):
		if self.state != "fight":
			self.output("%s runs in circles for a while" % self.name)
			self.tired()
		else:
			if random.randint(1, self.health+5) > random.randint(1, self.enemy.health):
				self.output("%s flees from %s." % (self.name, self.enemy.name))
				self.enemy = None
				self.state = "normal"
				self.tired()
			else: 
				self.output("%s couldn't escape from %s!" % (self.name, self.enemy.name))
				self.enemy_attacks()

	def explore(self):
		if self.state != "normal":
			self.output("%s is too busy right now!" % self.name)
			self.enemy_attacks()
		else:
			self.output("%s explores a new passage." % self.name)
			self.xp += 10
			self.passages_explored += 1
			num = random.randint(0, 10)
			if num > 7:
				self.enemy = Enemy(self)
				self.output("%s encounters %s [%d/%dHP]!" % (self.name, self.enemy.name, self.enemy.health, self.enemy.health_max))
				self.state = "fight"
			elif num > 3:
				self.treasure = random.choice(treasures)
				self.output("%s finds a treasure chest containing %s!" % (self.name, self.treasure.title()))
				if self.treasure != "nothing":
					self.totals[self.treasure] += 1
					if self.treasure in rare_items:
						self.xp += 100
					else:
						self.xp += 50
					self.inventory[self.treasure] += 1
				else:
					self.xp += 10
			else:
				if random.randint(0, 10) > 7:
					self.tired()

	def quit(self):
		quit()

	def tired(self):
		prev_health = self.health
		self.health = max(1, self.health-1)
		self.output("%s is tired. HP decreases by %d." % (self.name, prev_health - self.health), clear = False)

	def enemy_attacks(self):
		if self.enemy.do_damage(self):
			self.output("%s was killed by %s." % (self.name, self.enemy.name), clear = False)

	def clear(self):
		if idle:
			for i in range(80):
				self.output("")
		else:
			os.system("cls")

	def check_xp(self):
		if self.xp > self.req_xp:
			self.health += 1
			self.health_max += 1
			self.output("%s leveled up!" % self.name, clear = False)
			self.level += 1
			self.req_xp = (1.5 ** self.level) * 500

	def get_health(self):
		return player.health

	def get_enemy_health(self):
		return self.enemy.health

	def get_enemy_health_max(self):
		return self.enemy.health_max

	def get_enemy_name(self):
		return self.enemy.name

	def display_inventory(self):
		self.output("")
		for item in list(self.inventory.keys()):
			value = self.inventory[item]
			if value > 0:
				self.output("%s: %d" % (item.title(), value), clear = False)

	def output(self, text, clear=True):
		try:
			app.output(text, clear)
		except:
			pass

	def check_death(self):
		if self.get_health() == 0:
			self.output("%s died!\n" % self.name)
			self.output("%s's final stats:-" % self.name, clear = False)
			self.output("\tPassages explored: %d | Enemies slain: %d" % (self.passages_explored, self.enemies_killed), clear=False)
			for item in list(self.totals.keys()):
				if self.totals[item] > 0:
					self.output("\t%s: %d" % (item.title(), self.totals[item]), clear=False)
			self.game_over = True


class Enemy(Character):
	def __init__(self, player):
		Character.__init__(self)
		self.name = random.choice(enemies).title()
		self.health = random.randint(1, player.health_max)
		self.health_max = self.health

class GUI(Frame):
	def __init__(self, master, player):
		super(GUI, self).__init__(master)
		self.grid()
		self.name = ""
		self.name_widgets()

	def init_game(self):
		self.name_widgets_destroy()
		self.create_widgets()

	def name_widgets(self):
		self.name_lbl = Label(self, text = "Choose a name for your adventurer:")
		self.name_lbl.grid(row = 0, column = 0, sticky = W)
		self.name_entry = Entry(self)
		self.name_entry.grid(row = 0, column = 1, sticky = E)
		self.name_submit_bttn = Button(self, text = "Submit", command = self.get_name)
		self.name_submit_bttn.grid(row = 1, column = 0, columnspan=2, sticky = E)

	def name_widgets_destroy(self):
		self.name_lbl.grid_forget()
		self.name_entry.grid_forget()
		self.name_submit_bttn.grid_forget()

	def get_name(self):
		self.name = " ".join(x for x in self.name_entry.get().strip().split())
		player.set_name(self.name)
		self.init_game()

	def create_widgets(self):
		self.health_lbl = Label(self, text = "HP %d/%d" % (player.health, player.health_max), fg = "green")
		self.health_lbl.grid(row = 0, column = 0, sticky = W+E)
		self.enemy_health_lbl = Label(self, text = "", fg = "red")
		self.enemy_health_lbl.grid(row = 0, column = 2, sticky = W+E)
		self.xp_lbl = Label(self, text = "XP %d/%d" % (player.xp, player.req_xp), fg = "purple")
		self.xp_lbl.grid(row = 0, column = 1, sticky = W+E)
		self.level_lbl = Label(self, text = "Level: %d" % player.level, fg="green")
		self.level_lbl.grid(row = 1, column = 0, sticky = W+E)
		self.state_lbl = Label(self, text = "State: Exploring")
		self.state_lbl.grid(row = 1, column = 1, sticky = W+E)
		self.attack_bttn = Button(self, text = "\n Attack \n", command = lambda: self.action("attack"))
		self.attack_bttn.grid(row = 3, column = 0, sticky = W+E)
		self.explore_bttn = Button(self, text="\nExplore\n", command = lambda: self.action("explore"))
		self.explore_bttn.grid(row = 3, column = 1, sticky = W+E)
		self.heal_bttn = Button(self, text="\n  Heal  \n", command = lambda: self.action("heal"))
		self.heal_bttn.grid(row = 3, column = 2, sticky = W+E)
		self.rest_bttn = Button(self, text = "\n  Rest  \n", command = lambda: self.action("rest"))
		self.rest_bttn.grid(row = 4, column = 0, sticky = W+E)
		self.flee_bttn = Button(self, text = "\n  Flee  \n", command = lambda: self.action("flee"))
		self.flee_bttn.grid(row = 4, column = 1, sticky = W+E)
		self.inventory_bttn = Button(self, text = "\nInventory\n", command = lambda: self.action("inventory"))
		self.inventory_bttn.grid(row = 4, column = 2, sticky = W+E)
		self.placeholder_bttn1 = Button(self, text="\nPlaceholder1\n")
		self.placeholder_bttn1.grid(row = 3, column = 3, sticky = W+E)
		self.placeholder_bttn2 = Button(self, text="\nPlaceholder2\n")
		self.placeholder_bttn2.grid(row = 4, column = 3, sticky = W+E)
		self.message_out = Text(self, wrap=WORD, width = 50, height = 20)
		self.message_out.grid(row=10, column=0, columnspan = 4, sticky = S+W)
		self.message_out.config(state=DISABLED)
		self.message_out["font"]=("Arial", 10, "bold")

	def update_widgets(self):
		self.health_lbl["text"] = "HP %d/%d" % (player.health, player.health_max)
		self.xp_lbl["text"] = "XP %d/%d" % (player.xp, player.req_xp)
		self.level_lbl["text"] = "Level: %d" % player.level
		if player.state == "fight":
			state = "In Combat"
			self.enemy_health_lbl["text"] = "%s's HP %d/%d" % (player.get_enemy_name(), player.get_enemy_health(), player.get_enemy_health_max())
		else:
			state = "Exploring"
			self.enemy_health_lbl["text"] = ""
		self.state_lbl["text"] = "State: %s" % state
		self.message_out.yview(END)

	def action(self, a):
		if player.game_over == True:
			return
		command = a
		try:
			commands[command](player)
			player.check_xp()
			player.check_death()
			self.update_widgets()
		except KeyError:
			print("%s is confused." % player.name)

	def output(self, text, clear = True):
		self.message_out.config(state=NORMAL)
		if not clear:
			self.current_text = self.message_out.get(0.0, END).strip()
			self.current_text += "\n" + text
		else:
			self.current_text = text + "\n"
		self.message_out.delete(0.0, END)
		self.message_out.insert(0.0, self.current_text)
		self.message_out.config(state=DISABLED)


commands = {"help":Player.help,
			"attack":Player.attack,
			"status":Player.status,
			"rest":Player.rest,
			"flee":Player.flee,
			"explore":Player.explore,
			"quit":Player.quit,
			"heal":Player.heal,
			"clear":Player.clear,
			"inventory":Player.display_inventory}

locations = ["a dark cave", "a haunted mansion", "a ruined castle", "an ancient temple", "a misty forest", "a lost city"]

enemies = ["goblin", "bat", "zombie", "vampire", "werewolf", "spaghetti monster"] # this list can be expanded

treasures = ["potion of healing", "nothing", "gems", "coins", "potion of strength"]#, "moonlight crystal",\
			 #"augor of the darkmoon", "sunlight twinblades", "scroll of fortitude",\
			 #"bolas", "resurrection stone", "severed head", "dust"]
rare_items = ["gems", "coins"]

help_text = """\
Amazing RPG is a game about exploring dungeons and fighting enemies.

Items: 
	Healing Potions - Restore 2HP per use. You start with three of these. More can be found in treasure chests.
	Gems & Coins - Currency that can be used to purchase items from the shop. (WIP)

Combat:
	Attacking deals a random amount of damage.
	Characters have a random chance to dodge an attack.

Actions:
	Resting restores 1HP. There is a small chance of being woken up by an enemy, in which case no HP will be restored.
	You cannot rest while at full HP.

	Fleeing allows you to escape combat. This will cause you to become tired and will decrease your HP by a small amount.

	While exploring, you may come across empty rooms, treasure chests or enemies.

Leveling:
	You level up by gaining XP. Bonuses for leveling up include increased health and better loot.

	Killing enemies will give you 100XP.
	Finding rare treasure (Gems or Coins) will give you 50XP.
	Finding common treasure (Healing Potions) will give you 50XP.
	Finding useless treasure will give you 10XP.
	Finding empty rooms will give you 5XP.
"""

if __name__ == "__main__":
	root = Tk()
	root.resizable(width=False, height=False)
	root.geometry("350x400")
	root.title("Amazing RPG V0.71 - GUI")
	if "idlelib.run" in sys.modules:
		idle = True
	else:
		idle = False
	player = Player()
	app = GUI(root, player)
	location = random.choice(locations)
	player.output("%s enters %s in search of adventure!" % (player.name, location))
	root.mainloop()