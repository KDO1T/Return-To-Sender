#for game progression

import json
import os

import keyring
from cryptography.fernet import Fernet, InvalidToken

SAVES_DIR = os.path.join(os.getcwd(), "saves")
os.makedirs(SAVES_DIR, exist_ok=True)

KEYRING_SERVICE = "Return To Sender"
KEYRING_USERNAME = "save_encryption_key"

# Set to True when you want save files encrypted.
# Set to False while testing so you can open the JSON and inspect the saved data.
USE_ENCRYPTION = False


def get_encryption_key():
    # Store the encryption key in the operating system's keyring.
    key = keyring.get_password(KEYRING_SERVICE, KEYRING_USERNAME)

    if key is None:
        key = Fernet.generate_key().decode()
        keyring.set_password(KEYRING_SERVICE, KEYRING_USERNAME, key)

    return key.encode()


def get_fernet():
    return Fernet(get_encryption_key())


def get_save_path(slot_index):
    for filename in os.listdir(SAVES_DIR):
        if not filename.endswith(".json"):
            continue

        path = os.path.join(SAVES_DIR, filename)

        try:
            with open(path, "r") as file:
                data = json.load(file)

            if data.get("slot_index") == slot_index:
                return path

        except (json.JSONDecodeError, OSError):
            pass

    return os.path.join(SAVES_DIR, f"slot_{slot_index}.json")

#write
def save_game(
    slot_index,
    player,
    player_rect,
    brightness=50,
    current_stage=None,
    map_seed=None,
    spritesheet=None,
    zombie_count=None
):
    save_path = get_save_path(slot_index)

    # Keep the existing save slot name when updating the save.
    slot_name = f"Save {slot_index + 1}"

    if os.path.exists(save_path):
        try:
            with open(save_path, "r") as file:
                existing_data = json.load(file)

            # New/renamed saves store the name outside the encrypted data.
            if "name" in existing_data:
                slot_name = existing_data["name"]

            # Existing encrypted saves may store the name inside the encrypted data.
            elif "encrypted_data" in existing_data:
                try:
                    decrypted_data = get_fernet().decrypt(
                        existing_data["encrypted_data"].encode("utf-8")
                    )
                    existing_save = json.loads(
                        decrypted_data.decode("utf-8")
                    )

                    slot_name = existing_save.get(
                        "name",
                        slot_name
                    )

                except (InvalidToken, ValueError, TypeError):
                    pass

        except (json.JSONDecodeError, OSError):
            pass

    data = {
        "slot_index": slot_index,
        "name": slot_name,
        "brightness": brightness,
        "player": {
            "Name": player.Name,
            "HP": player.HP,
            "max_HP": player.max_HP,
            "base_ATK": player.base_ATK,
            "CRIT_DMG": player.CRIT_DMG,
            "CRIT_CHANCE": player.CRIT_CHANCE,
            "LEVEL": player.LEVEL,
            "EXP": player.EXP,
            "DOLLARS": player.DOLLARS,
            "S_COIN": player.S_COIN
        },
        "position": {
            "x": player_rect.x,
            "y": player_rect.y
        },
        "world": {
            "current_stage": current_stage,
            "map_seed": map_seed,
            "spritesheet": spritesheet,
            "zombie_count": zombie_count
        }
    }

    with open(save_path, "w") as file:
        if USE_ENCRYPTION:
            encrypted_data = get_fernet().encrypt(
                json.dumps(data).encode("utf-8")
            )

            json.dump({
                "slot_index": slot_index,
                "name": slot_name,
                "encrypted_data": encrypted_data.decode("utf-8")
            }, file, indent=4)
        else:
            # Plain JSON makes it easy to inspect exactly what the game saved.
            json.dump(data, file, indent=4)

#read
def load_game(slot_index, player, player_rect, default_brightness=50):
    path = get_save_path(slot_index)

    if not os.path.exists(path):
        save_game(slot_index, player, player_rect, default_brightness)
        return default_brightness, {}

    try:
        with open(path, "r") as file:
            file_data = json.load(file)
    except (json.JSONDecodeError, OSError):
        return default_brightness, {}

    # Encrypted save format.
    if "encrypted_data" in file_data:
        try:
            decrypted_data = get_fernet().decrypt(
                file_data["encrypted_data"].encode("utf-8")
            )
            data = json.loads(decrypted_data.decode("utf-8"))
        except (InvalidToken, ValueError, TypeError):
            # The save was modified or cannot be decrypted.
            return default_brightness, {}


    else:
        data = file_data

        # Resave old plaintext saves using the current encryption setting
        try:
            player_data = data.get("player", {})
            player.Name = player_data.get("Name")
            saved_hp = player_data.get("HP")
            player.HP = saved_hp if saved_hp is not None else player.HP
            saved_max_hp = player_data.get("max_HP")
            player.max_HP = saved_max_hp if saved_max_hp is not None else player.max_HP
            saved_base_atk = player_data.get("base_ATK", player_data.get("ATK"))
            player.base_ATK = saved_base_atk if saved_base_atk is not None else player.base_ATK
            player.CRIT_DMG = player_data.get("CRIT_DMG")
            player.CRIT_CHANCE = player_data.get("CRIT_CHANCE")
            player.LEVEL = player_data.get("LEVEL")
            player.EXP = player_data.get("EXP")
            player.DOLLARS = player_data.get("DOLLARS")
            player.S_COIN = player_data.get("S_COIN")

            position = data.get("position", {})
            player_rect.x = position.get("x", player_rect.x)
            player_rect.y = position.get("y", player_rect.y)

            saved_brightness = data.get("brightness", default_brightness)
            world_data = data.get("world", {})
            save_game(
                slot_index,
                player,
                player_rect,
                saved_brightness,
                world_data.get("current_stage"),
                world_data.get("map_seed"),
                world_data.get("spritesheet"),
                world_data.get("zombie_count")
            )
            return max(0, min(100, saved_brightness)), world_data
        except (AttributeError, TypeError, ValueError):
            return default_brightness, {}

    player_data = data.get("player", {})

    player.Name = player_data.get("Name")
    saved_hp = player_data.get("HP")
    player.HP = saved_hp if saved_hp is not None else player.HP
    saved_max_hp = player_data.get("max_HP")
    player.max_HP = saved_max_hp if saved_max_hp is not None else player.max_HP
    saved_base_atk = player_data.get("base_ATK", player_data.get("ATK"))
    player.base_ATK = saved_base_atk if saved_base_atk is not None else player.base_ATK
    player.CRIT_DMG = player_data.get("CRIT_DMG")
    player.CRIT_CHANCE = player_data.get("CRIT_CHANCE")
    player.LEVEL = player_data.get("LEVEL")
    player.EXP = player_data.get("EXP")
    player.DOLLARS = player_data.get("DOLLARS")
    player.S_COIN = player_data.get("S_COIN")

    position = data.get("position", {})
    player_rect.x = position.get("x", player_rect.x)
    player_rect.y = position.get("y", player_rect.y)

    saved_brightness = data.get("brightness", default_brightness)
    world_data = data.get("world", {})
    if not isinstance(world_data, dict):
        world_data = {}
    return max(0, min(100, saved_brightness)), world_data