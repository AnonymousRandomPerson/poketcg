#!/usr/bin/env python

from __future__ import print_function

import argparse
import sys

from constants import boosters
from constants import cards
from constants import decks
from constants import directions
from constants import events
from constants import maps
from constants import npcs
from constants import sfxs
from constants import songs

args = None
rom = None
symbols = None
texts = None

# script command names and parameter lists
script_commands = {
	0xe7: { "name": "start_script",                               "params": [] },

	0x00: { "name": "end_script",                                 "params": [] },
	0x01: { "name": "close_advanced_text_box",                    "params": [] },
	0x02: { "name": "print_npc_text",                             "params": [ "text" ] },
	0x03: { "name": "Func_ccdc",                                  "params": [ "text" ] }, # print text without npc name
	0x04: { "name": "ask_question_jump",                          "params": [ "text", "label" ] },
	0x05: { "name": "start_duel",                                 "params": [ "prizes", "deck", "song" ] },
	0x06: { "name": "print_variable_npc_text",                    "params": [ "text", "text" ] },
	0x07: { "name": "Func_cda8",                                  "params": [ "text", "text" ] }, # print variable text without npc name
	0x08: { "name": "print_text_quit_fully",                      "params": [ "text" ] },
	0x09: { "name": "Func_cdcb",                                  "params": [] }, # unload active npc
	0x0a: { "name": "move_active_npc_by_direction",               "params": [ "movement_table" ] },
	0x0b: { "name": "close_text_box",                             "params": [] },
	0x0c: { "name": "give_booster_packs",                         "params": [ "booster", "booster", "booster" ] },
	0x0d: { "name": "jump_if_card_owned",                         "params": [ "card", "label" ] },
	0x0e: { "name": "jump_if_card_in_collection",                 "params": [ "card", "label" ] },
	0x0f: { "name": "give_card",                                  "params": [ "card" ] },
	0x10: { "name": "take_card",                                  "params": [ "card" ] },
	0x11: { "name": "Func_cf53",                                  "params": [ "label" ] }, # jump if any energy cards in collection
	0x12: { "name": "Func_cf7b",                                  "params": [] }, # remove all energy cards from collection
	0x13: { "name": "jump_if_enough_cards_owned",                 "params": [ "word_decimal", "label" ] },
	0x14: { "name": "fight_club_pupil_jump",                      "params": [ "label", "label", "label", "label", "label" ] },
	0x15: { "name": "Func_cfc6",                                  "params": [ "direction" ] }, # set active npc direction
	0x16: { "name": "Func_cfd4",                                  "params": [] }, # pick next man1 requested card (EVENT_FLAG_2B)
	0x17: { "name": "Func_d00b",                                  "params": [] }, # get man1 requested card name text (EVENT_FLAG_2B)
	0x18: { "name": "Func_d025",                                  "params": [ "label" ] }, # jump if man1 requested card owned (EVENT_FLAG_2B)
	0x19: { "name": "Func_d032",                                  "params": [ "label" ] }, # jump if man1 requested card in collection (EVENT_FLAG_2B)
	0x1a: { "name": "Func_d03f",                                  "params": [] }, # remove man1 requested card from collection (EVENT_FLAG_2B)
	0x1b: { "name": "script_jump",                                "params": [ "label" ] },
	0x1c: { "name": "try_give_medal_pc_packs",                    "params": [] },
	0x1d: { "name": "set_player_direction",                       "params": [ "direction" ] },
	0x1e: { "name": "move_player",                                "params": [ "direction", "byte_decimal" ] },
	0x1f: { "name": "show_card_received_screen",                  "params": [ "card" ] },
	0x20: { "name": "set_dialog_npc",                             "params": [ "npc" ] },
	0x21: { "name": "set_next_npc_and_script",                    "params": [ "npc", "label" ] },
	0x22: { "name": "Func_d095",                                  "params": [ "byte", "byte", "byte" ] }, # set sprite attributes LOADED_NPC_FIELD_05 and LOADED_NPC_FIELD_06
	0x23: { "name": "Func_d0be",                                  "params": [ "byte_decimal", "byte_decimal" ] }, # coords, set active npc coords
	0x24: { "name": "do_frames",                                  "params": [ "byte_decimal" ] },
	0x25: { "name": "Func_d0d9",                                  "params": [ "byte_decimal", "byte_decimal", "label" ] }, # coords, jump if active npc coords match
	0x26: { "name": "jump_if_player_coords_match",                "params": [ "byte_decimal", "byte_decimal", "label" ] },
	0x27: { "name": "move_active_npc",                            "params": [ "movement" ] },
	0x28: { "name": "give_one_of_each_trainer_booster",           "params": [] },
	0x29: { "name": "Func_d103",                                  "params": [ "npc", "label" ] }, # jump if npc loaded
	0x2a: { "name": "Func_d125",                                  "params": [ "event" ] }, # show medal received screen ?
	0x2b: { "name": "Func_d135",                                  "params": [ "byte" ] }, # load current map name into tx ram slot
	0x2c: { "name": "Func_d16b",                                  "params": [ "byte" ] }, # load active npc name into tx ram slot
	0x2d: { "name": "Func_cd4f",                                  "params": [ "prizes", "deck", "song" ] }, # start challenge hall duel
	0x2e: { "name": "Func_cd94",                                  "params": [ "text", "text", "text" ] }, # print text based on challenge cup number
	0x2f: { "name": "move_wram_npc",                              "params": [ "movement" ] },
	0x30: { "name": "Func_cdd8",                                  "params": [] }, # unload challenge hall npc
	0x31: { "name": "Func_cdf5",                                  "params": [ "byte", "byte" ] }, # coords, set challenge hall npc coords
	0x32: { "name": "Func_d195",                                  "params": [] }, # pick challenge hall opponent
	0x33: { "name": "Func_d1ad",                                  "params": [] }, # open menu
	0x34: { "name": "Func_d1b3",                                  "params": [] }, # pick challenge cup prize card
	0x35: { "name": "quit_script_fully",                          "params": [] },
	0x36: { "name": "Func_d244",                                  "params": [ "byte" ] }, # replace map blocks (dech machines, pokemon dome doors, hall of honor doors, challenge machine)
	0x37: { "name": "choose_deck_to_duel_against",                "params": [] },
	0x38: { "name": "open_deck_machine",                          "params": [ "byte" ] },
	0x39: { "name": "choose_starter_deck",                        "params": [] },
	0x3a: { "name": "enter_map",                                  "params": [ "byte", "map", "byte_decimal", "byte_decimal", "direction" ] },
	0x3b: { "name": "move_npc",                                   "params": [ "npc", "movement" ] },
	0x3c: { "name": "Func_d209",                                  "params": [] }, # pick legendary card
	0x3d: { "name": "Func_d38f",                                  "params": [ "byte" ] }, # flash screen (bool arg, true to stay white)
	0x3e: { "name": "Func_d396",                                  "params": [ "byte" ] }, # save game (bool arg, true to go back to dr mason lab)
	0x3f: { "name": "Func_cd76",                                  "params": [] }, # battle center
	0x40: { "name": "Func_d39d",                                  "params": [ "byte" ] }, # gift center (bool arg, false for menu, true to executing selection)
	0x41: { "name": "Func_d3b9",                                  "params": [] }, # play credits
	0x42: { "name": "try_give_pc_pack",                           "params": [ "byte" ] },
	0x43: { "name": "script_nop",                                 "params": [] },
	0x44: { "name": "Func_d3d4",                                  "params": [] }, # give starter deck
	0x45: { "name": "Func_d3e0",                                  "params": [] }, # walk player to dr mason lab
	0x46: { "name": "Func_d3fe",                                  "params": [ "song" ] }, # override song
	0x47: { "name": "Func_d408",                                  "params": [ "song" ] }, # set default song
	0x48: { "name": "play_song",                                  "params": [ "song" ] },
	0x49: { "name": "play_sfx",                                   "params": [ "sfx" ] },
	0x4a: { "name": "pause_song",                                 "params": [] },
	0x4b: { "name": "resume_song",                                "params": [] },
	0x4c: { "name": "Func_d41d",                                  "params": [] }, # play default song
	0x4d: { "name": "wait_for_song_to_finish",                    "params": [] },
	0x4e: { "name": "Func_d435",                                  "params": [ "byte" ] }, # record master win (8 clubs plus ronald card master)
	0x4f: { "name": "ask_question_jump_default_yes",              "params": [ "text", "label" ] },
	0x50: { "name": "show_sam_normal_multichoice",                "params": [] },
	0x51: { "name": "show_sam_tutorial_multichoice",              "params": [] },
	0x52: { "name": "Func_d43d",                                  "params": [] }, # challenge machine
	0x53: { "name": "end_script_2",                               "params": [] },
	0x54: { "name": "end_script_3",                               "params": [] },
	0x55: { "name": "end_script_4",                               "params": [] },
	0x56: { "name": "end_script_5",                               "params": [] },
	0x57: { "name": "end_script_6",                               "params": [] },
	0x58: { "name": "script_set_flag_value",                      "params": [ "event", "byte" ] },
	0x59: { "name": "jump_if_flag_zero_1",                        "params": [ "event", "label" ] },
	0x5a: { "name": "jump_if_flag_nonzero_1",                     "params": [ "event", "label" ] },
	0x5b: { "name": "jump_if_flag_equal",                         "params": [ "event", "byte", "label" ] },
	0x5c: { "name": "jump_if_flag_not_equal",                     "params": [ "event", "byte", "label" ] },
	0x5d: { "name": "jump_if_flag_not_less_than",                 "params": [ "event", "byte", "label" ] },
	0x5e: { "name": "jump_if_flag_less_than",                     "params": [ "event", "byte", "label" ] },
	0x5f: { "name": "max_out_flag_value",                         "params": [ "event" ] },
	0x60: { "name": "zero_out_flag_value",                        "params": [ "event" ] },
	0x61: { "name": "jump_if_flag_nonzero_2",                     "params": [ "event", "label"] },
	0x62: { "name": "jump_if_flag_zero_2",                        "params": [ "event", "label" ] },
	0x63: { "name": "increment_flag_value",                       "params": [ "event" ] },
	0x64: { "name": "end_script_7",                               "params": [] },
	0x65: { "name": "end_script_8",                               "params": [] },
	0x66: { "name": "end_script_9",                               "params": [] },
	0x67: { "name": "end_script_10",                              "params": [] },
}

quit_commands = [
	0x00,
	0x08,
	0x1b,
	0x35,
	0x53,
	0x54,
	0x55,
	0x56,
	0x57,
	0x64,
	0x65,
	0x66,
	0x67,
]

# length in bytes of each type of parameter
param_lengths = {
	"byte":           1,
	"byte_decimal":   1,
	"booster":        1,
	"card":           1,
	"deck":           1,
	"direction":      1,
	"event":          1,
	"map":            1,
	"npc":            1,
	"prizes":         1,
	"sfx":            1,
	"song":           1,
	"word_decimal":   2,
	"movement":       2,
	"movement_table": 2,
	"text":           2,
	"label":          2,
}

def get_bank(address):
	return int(address / 0x4000)

def get_relative_address(address):
	if address < 0x4000:
		return address
	return (address % 0x4000) + 0x4000

# get absolute pointer stored at an address in the rom
# if bank is None, assumes the pointer refers to the same bank as the bank it is located in
def get_pointer(address, bank=None):
	raw_pointer = rom[address + 1] * 0x100 + rom[address]
	if raw_pointer < 0x4000:
		bank = 0
	if bank is None:
		bank = get_bank(address)
	return (raw_pointer % 0x4000) + bank * 0x4000

def make_address_comment(address):
	return ": ; {:x} ({:x}:{:x})\n".format(address, get_bank(address), get_relative_address(address))

def make_blob(start, output, end=None):
	return { "start": start, "output": output, "end": end if end else start }

def dump_movement(address):
	blobs = []
	label = "NPCMovement_{:x}".format(address)
	if address in symbols:
		label = symbols[address]
	blobs.append(make_blob(address, label + make_address_comment(address)))
	while 1:
		movement = rom[address]
		if movement == 0xff:
			blobs.append(make_blob(address, "\tdb ${:02x}\n\n".format(movement), address + 1))
			break
		if movement == 0xfe:
			jump = rom[address + 1]
			if jump > 127:
				jump -= 256
			blobs.append(make_blob(address, "\tdb ${:02x}, {}\n\n".format(movement, jump), address + 2))
			break
		blobs.append(make_blob(address, "\tdb {}".format(directions[movement & 0b01111111]) + (" | NO_MOVE\n" if movement & 0b10000000 else "\n"), address + 1))
		address += 1
	return blobs

def dump_movement_table(address):
	blobs = []
	label = "NPCMovementTable_{:x}".format(address)
	if address in symbols:
		label = symbols[address]
	blobs.append(make_blob(address, label + make_address_comment(address)))
	for i in range(4):
		pointer = get_pointer(address)
		blobs.append(make_blob(address, "\tdw NPCMovement_{:x}\n".format(pointer) + ("\n" if i == 3 else ""), address + 2))
		blobs += dump_movement(pointer)
		address += 2
	return blobs

# parse a script starting at the given address
# returns a list of all commands
def dump_script(start_address, address=None, visited=set()):
	blobs = []
	branches = set()
	if address is None:
		label = "Script_{:x}".format(start_address)
		if start_address in symbols:
			label = symbols[start_address]
		blobs.append(make_blob(start_address, label + make_address_comment(start_address)))
		address = start_address
	else:
		label = ".ows_{:x}\n".format(address)
		if address in symbols:
			label = symbols[address]
			if label.startswith("."):
				label += "\n"
			else:
				label += make_address_comment(address)
		blobs.append(make_blob(address, label))
	if address in visited:
		return blobs
	visited.add(address)
	while 1:
		command_address = address
		command_id = rom[command_address]
		command = script_commands[command_id]
		address += 1
		macro_mode = not command["name"].startswith("Func_")
		if macro_mode:
			output = "\t{}".format(command["name"])
		else:
			output = "\trun_command {}".format(command["name"])
		# print all params for current command
		for i in range(len(command["params"])):
			param = rom[address]
			param_type = command["params"][i]
			param_length = param_lengths[param_type]
			if param_type == "byte":
				if not macro_mode:
					output += "\n\tdb"
				output += " ${:02x}".format(param)
			elif param_type == "byte_decimal":
				if not macro_mode:
					output += "\n\tdb"
				output += " {}".format(param)
			elif param_type == "booster":
				if not macro_mode:
					output += "\n\tdb"
				output += " {}".format(boosters[param])
			elif param_type == "card":
				if not macro_mode:
					output += "\n\tdb"
				output += " {}".format(cards[param])
			elif param_type == "deck":
				if not macro_mode:
					output += "\n\tdb"
				output += " {}".format(decks[param])
			elif param_type == "direction":
				if not macro_mode:
					output += "\n\tdb"
				output += " {}".format(directions[param])
			elif param_type == "event":
				if not macro_mode:
					output += "\n\tdb"
				output += " {}".format(events[param])
			elif param_type == "map":
				if not macro_mode:
					output += "\n\tdb"
				output += " {}".format(maps[param])
			elif param_type == "npc":
				if not macro_mode:
					output += "\n\tdb"
				output += " {}".format(npcs[param])
			elif param_type == "prizes":
				if not macro_mode:
					output += "\n\tdb"
				output += " PRIZES_{}".format(param)
			elif param_type == "sfx":
				if not macro_mode:
					output += "\n\tdb"
				output += " {}".format(sfxs[param])
			elif param_type == "song":
				if not macro_mode:
					output += "\n\tdb"
				output += " {}".format(songs[param])
			elif param_type == "word_decimal":
				if not macro_mode:
					output += "\n\tdw"
				output += " {}".format(param + rom[address + 1] * 0x100)
			elif param_type == "movement":
				param = get_pointer(address)
				label = "NPCMovement_{:x}".format(param)
				if param in symbols:
					label = symbols[param]
				if not macro_mode:
					output += "\n\tdw"
				output += " {}".format(label)
				blobs += dump_movement(param)
			elif param_type == "movement_table":
				param = get_pointer(address)
				label = "NPCMovementTable_{:x}".format(param)
				if param in symbols:
					label = symbols[param]
				if not macro_mode:
					output += "\n\tdw"
				output += " {}".format(label)
				blobs += dump_movement_table(param)
			elif param_type == "text":
				text_id = param + rom[address + 1] * 0x100
				if not macro_mode:
					if text_id == 0x0000:
						output += "\n\tdw"
					else:
						output += "\n\ttx"
				if text_id == 0x0000:
					output += " NULL"
				else:
					output += " {}".format(texts[text_id])
			elif param_type == "label":
				param = get_pointer(address)
				if param == 0x0000:
					label = "NULL"
				elif param == start_address:
					label = "Script_{:x}".format(param)
					if param in symbols:
						label = symbols[param]
				else:
					label = ".ows_{:x}".format(param)
					if param in symbols:
						label = symbols[param]
					if param > start_address or args.allow_backward_jumps:
						branches.add(param)
				if not macro_mode:
					output += "\n\tdw"
				output += " {}".format(label)
			address += param_length
			if macro_mode and i < len(command["params"]) - 1:
				output += ","
		output += "\n"
		blobs.append(make_blob(command_address, output, address))
		if command_id in quit_commands:
			if rom[address] == 0xc9:
				blobs.append(make_blob(address, "\tret\n", address + 1))
				address += 1
			blobs.append(make_blob(address, "; 0x{:x}\n\n".format(address)))
			break
	for branch in branches:
		blobs += dump_script(start_address, branch, visited)
	return blobs

def fill_gap(start, end):
	output = ""
	for address in range(start, end):
		output += "\tdb ${:x}\n".format(rom[address])
	output += "\n"
	return output

def sort_and_filter(blobs):
	blobs.sort(key=lambda b: (b["start"], b["end"], not b["output"].startswith(";")))
	filtered = []
	for blob, next in zip(blobs, blobs[1:]+[None]):
		if next and blob["start"] == next["start"] and blob["output"] == next["output"]:
			continue
		if next and blob["end"] < next["start"] and get_bank(blob["end"]) == get_bank(next["start"]):
			if args.fill_gaps:
				blob["output"] += fill_gap(blob["end"], next["start"])
			else:
				blob["output"] += "; gap from 0x{:x} to 0x{:x}\n\n".format(blob["end"], next["start"])
		filtered.append(blob)
	if len(filtered) > 0:
		filtered[-1]["output"] = filtered[-1]["output"].rstrip("\n")
	return filtered

def find_unreachable_labels(input):
	scope = ""
	label_scopes = {}
	local_labels = set()
	local_references = set()
	unreachable_labels = set()
	for line in input.split("\n"):
		line = line.split(";")[0].rstrip()
		if line.startswith("\t"):
			for word in [x.rstrip(",") for x in line.split()]:
				if word.startswith("."):
					local_references.add(word)
		elif line.startswith("."):
			label = line.split()[0]
			local_labels.add(label)
			label_scopes[label] = scope
		elif line.endswith(":"):
			for label in local_references:
				if label not in local_labels:
					unreachable_labels.add(label)
			scope = line[:-1]
			local_labels = set()
			local_references = set()
	for label in local_references:
		if label not in local_labels:
			unreachable_labels.add(label)
	unreachable_labels = list(unreachable_labels)
	for i in range(len(unreachable_labels)):
		label = unreachable_labels[i]
		unreachable_labels[i] = { "scope": label_scopes.get(label, ""), "label": label }
	return unreachable_labels

def fix_unreachable_labels(input, unreachable_labels):
	scope = ""
	output = ""
	for line in input.split("\n"):
		stripped_line = line.split(";")[0].rstrip()
		if line.startswith("\t"):
			for label in unreachable_labels:
				if label["label"] in line and label["scope"] != scope:
					line = line.replace(label["label"], label["scope"] + label["label"])
		elif stripped_line.endswith(":"):
			scope = stripped_line[:-1]
		output += line + "\n"
	output = output.rstrip("\n")
	return output

def load_symbols(symfile):
	sym = {}
	for line in open(symfile):
		line = line.split(";")[0].strip()
		# NOTE: only worry about bank 3 symbols for now
		if line.startswith("03:"):
			bank_address, label = line.split(" ")[:2]
			bank, address = bank_address.split(":")
			address = (int(address, 16) % 0x4000) + int(bank, 16) * 0x4000
			if "." in label:
				label = "." + label.split(".")[1]
			sym[address] = label
	return sym

def load_texts(txfile):
	tx = [None]
	for line in open(txfile):
		if line.startswith("\ttextpointer"):
			tx.append(line.split()[1])
	return tx

if __name__ == "__main__":
	ap = argparse.ArgumentParser(description="Pokemon TCG Script Extractor")
	ap.add_argument("-b", "--allow-backward-jumps", action="store_true", help="extract scripts that are found before the starting address")
	ap.add_argument("-f", "--fix-unreachable", action="store_true", help="fix unreachable labels that are referenced from the wrong scope")
	ap.add_argument("-g", "--fill-gaps", action="store_true", help="use 'db's to fill the gaps between visited locations")
	ap.add_argument("-i", "--ignore-errors", action="store_true", help="silently proceed to the next address if an error occurs")
	ap.add_argument("-r", "--rom", default="baserom.gbc", help="rom file to extract script from")
	ap.add_argument("-s", "--symfile", default="poketcg.sym", help="symfile to extract symbols from")
	ap.add_argument("addresses", nargs="+", help="addresses to extract from")
	args = ap.parse_args()
	rom = bytearray(open(args.rom, "rb").read())
	symbols = load_symbols(args.symfile)
	texts = load_texts("src/text/text_offsets.asm")
	blobs = []
	for address in args.addresses:
		try:
			blobs += dump_script(int(address, 16))
		except:
			print("Parsing script failed: 0x{:x}".format(int(address, 16)), file=sys.stderr)
			if not args.ignore_errors:
				raise
	blobs = sort_and_filter(blobs)
	output = ""
	for blob in blobs:
		output += blob["output"]
	if args.fix_unreachable:
		unreachable_labels = find_unreachable_labels(output)
		output = fix_unreachable_labels(output, unreachable_labels)
	print(output)
