import pygame

from spritesheet import Spritesheet

# ==================================================
# BACKEND DATA & CONSTANTS
# ==================================================
COL_BG = (15, 17, 23)
COL_PANEL = (24, 28, 38)
COL_PANEL_BORDER = (50, 58, 75)
COL_TEXT = (240, 243, 250)
COL_MUTED = (130, 140, 160)
COL_DIM = (70, 78, 95)
COL_ACCENT = (240, 80, 80)
COL_SOUL = (80, 220, 200)
COL_BAD = (240, 80, 80)
COL_GOOD = (100, 220, 120)

HUB_POS = (320, 160)  # Central origin point

BRANCHES = {
    "COMBAT":   {"color": (240, 80, 80),   "label_pos": (200, 44)},
    "SURVIVAL": {"color": (80, 210, 120),  "label_pos": (213, 222)},
    "MOVEMENT": {"color": (70, 170, 240),  "label_pos": (320, 252)},
    "ECONOMY":  {"color": (240, 190, 60),  "label_pos": (400, 222)},
    "WEAPONS":  {"color": (180, 110, 240), "label_pos": (440, 44)},
}

SKILLS = {
    # ---------------- COMBAT ----------------
    "attack_damage": {
        "name": "Attack Damage", "branch": "COMBAT", "cost": 5, "pos": (268, 125),
        "parent": None, "requires_ranged": False,
        "desc": "+20% damage on all attacks.",
        "effects": {"damage_pct": 0.20},
    },
    "crit_chance": {
        "name": "Critical Chance", "branch": "COMBAT", "cost": 10, "pos": (213, 125),
        "parent": "attack_damage", "requires_ranged": False,
        "desc": "+10% chance to land a critical hit.",
        "effects": {"crit_chance": 0.10},
    },
    "crit_damage": {
        "name": "Critical Damage", "branch": "COMBAT", "cost": 20, "pos": (158, 125),
        "parent": "crit_chance", "requires_ranged": False,
        "desc": "Critical hits deal +50% bonus damage.",
        "effects": {"crit_damage": 0.50},
    },
    # ---------------- SURVIVAL ----------------
    "max_health": {
        "name": "Maximum Health", "branch": "SURVIVAL", "cost": 5, "pos": (268, 195),
        "parent": None, "requires_ranged": False,
        "desc": "+20 maximum HP.",
        "effects": {"max_hp": 20},
    },
    "damage_reduction": {
        "name": "Damage Reduction", "branch": "SURVIVAL", "cost": 12, "pos": (213, 195),
        "parent": "max_health", "requires_ranged": False,
        "desc": "Take 15% less damage from hits.",
        "effects": {"damage_reduction": 0.15},
    },
    # ---------------- MOVEMENT ----------------
    "movement_speed": {
        "name": "Movement Speed", "branch": "MOVEMENT", "cost": 10, "pos": (320, 220),
        "parent": None, "requires_ranged": False,
        "desc": "Run 25% faster.",
        "effects": {"move_speed_bonus": 1},
    },
    # ---------------- ECONOMY ----------------
    "shop_expansion": {
        "name": "Shop Expansion", "branch": "ECONOMY", "cost": 8, "pos": (372, 195),
        "parent": None, "requires_ranged": False,
        "desc": "Shops stock 1 extra item.",
        "effects": {"shop_slots": 1},
    },
    "purchase_limit": {
        "name": "Increased Purchase Limit", "branch": "ECONOMY", "cost": 16, "pos": (427, 195),
        "parent": "shop_expansion", "requires_ranged": False,
        "desc": "Buy 1 more of each item per visit.",
        "effects": {"purchase_limit": 1},
    },
    # ---------------- WEAPONS ----------------
    "blade_damage": {
        "name": "Blade Damage", "branch": "WEAPONS", "cost": 8, "pos": (372, 125),
        "parent": None, "requires_ranged": False,
        "desc": "+15% damage with the blade.",
        "effects": {"damage_pct": 0.15},
    },
    "ranged_damage": {
        "name": "Ranged Damage", "branch": "WEAPONS", "cost": 25, "pos": (372, 80),
        "parent": "blade_damage", "requires_ranged": True,
        "desc": "+20% ranged weapon damage.",
        "effects": {"ranged_damage_pct": 0.20},
    },
    "ranged_capacity": {
        "name": "Ranged Capacity", "branch": "WEAPONS", "cost": 35, "pos": (427, 80),
        "parent": "ranged_damage", "requires_ranged": True,
        "desc": "+2 ammo for the ranged weapon.",
        "effects": {"ranged_capacity": 2},
    },
}

EFFECT_KEYS = (
    "damage_pct", "crit_chance", "crit_damage", "max_hp",
    "damage_reduction", "move_speed_bonus", "shop_slots",
    "purchase_limit", "ranged_damage_pct", "ranged_capacity",
)



# ==================================================
# BACKEND STATE MANAGER
# ==================================================
class SkillTreeState:
    def __init__(self, player):
        self.player = player

        saved = getattr(player, "skill_tree_purchased", None) or []
        clean = []
        for skill_id in saved:
            if skill_id in SKILLS and skill_id not in clean:
                clean.append(skill_id)
        player.skill_tree_purchased = clean

        if not hasattr(player, "ranged_unlocked"):
            player.ranged_unlocked = False

    def get_purchased(self):
        return self.player.skill_tree_purchased

    def get_coins(self):
        return int(getattr(self.player, "S_COIN", 0) or 0)

    def add_soul_coins(self, amount=50):
        current = self.get_coins()
        self.player.S_COIN = current + amount

    def is_ranged_unlocked(self):
        return bool(getattr(self.player, "ranged_unlocked", False))

    def unlock_ranged_weapon(self):
        self.player.ranged_unlocked = True

    def status(self, skill_id):
        if skill_id not in SKILLS:
            return "locked"
        skill = SKILLS[skill_id]
        purchased = self.get_purchased()

        if skill_id in purchased:
            return "purchased"
        if skill["requires_ranged"] and not self.is_ranged_unlocked():
            return "sealed"
        parent = skill["parent"]
        if parent is not None and parent not in purchased:
            return "locked"
        return "available"

    def status_text(self, skill_id):
        state = self.status(skill_id)
        skill = SKILLS[skill_id]
        coins = self.get_coins()

        if state == "purchased":
            return "UNLOCKED", COL_GOOD
        if state == "sealed":
            return "SEALED - Unlocks after final boss", BRANCHES["WEAPONS"]["color"]
        if state == "locked":
            return f"LOCKED - Requires {SKILLS[skill['parent']]['name']}", COL_MUTED
        if coins < skill["cost"]:
            return f"AVAILABLE - Need {skill['cost'] - coins} more coins", COL_ACCENT
        return "AVAILABLE", (240, 190, 60)

    def can_buy(self, skill_id):
        return self.status(skill_id) == "available" and self.get_coins() >= SKILLS[skill_id]["cost"]

    def buy(self, skill_id):
        state = self.status(skill_id)
        skill = SKILLS[skill_id]
        coins = self.get_coins()

        if state == "purchased":
            return False, "Already unlocked."
        if state == "sealed":
            return False, "Defeat the final boss first."
        if state == "locked":
            return False, f"Unlock {SKILLS[skill['parent']]['name']} first."
        if coins < skill["cost"]:
            return False, "Not enough Soul Coins."

        self.player.S_COIN = coins - skill["cost"]
        self.get_purchased().append(skill_id)
        return True, f"{skill['name']} unlocked!"

    def effects(self):
        totals = {key: 0 for key in EFFECT_KEYS}
        for skill_id in self.get_purchased():
            for key, value in SKILLS[skill_id]["effects"].items():
                totals[key] += value
        return totals


def apply_skill_effects(player, tree, heal_on_gain=True):
    fx = tree.effects()

    # Max HP
    old_bonus = getattr(player, "bonus_max_HP", 0)
    new_bonus = int(fx["max_hp"])
    delta = new_bonus - old_bonus
    player.max_HP += delta
    if heal_on_gain and delta > 0:
        player.HP += delta
    player.HP = min(player.HP, player.max_HP)
    player.bonus_max_HP = new_bonus

    # Combat stats
    player.damage_mult = 1.0 + fx["damage_pct"]
    player.crit_chance_bonus = fx["crit_chance"]
    player.crit_dmg_bonus = fx["crit_damage"]


    # Survival stats
    player.damage_reduction = min(0.9, fx["damage_reduction"])

    # Movement speed
    player.move_speed = getattr(player, "base_move_speed", 4) + int(fx["move_speed_bonus"])

    player.skill_effects = fx

    # Economy
    player.shop_slots = int(fx["shop_slots"])
    player.purchase_limit = int(fx["purchase_limit"])

    player.skill_effects = fx

# ==================== FRONTEND ====================

def blend_color(c1, c2, factor):
    """Blends two RGB color tuples cleanly without math module."""
    return (
        int(c1[0] + (c2[0] - c1[0]) * factor),
        int(c1[1] + (c2[1] - c1[1]) * factor),
        int(c1[2] + (c2[2] - c1[2]) * factor),
    )


def load_font(path, size):
    """Loads custom font with fallback to standard system font."""
    try:
        return pygame.font.Font(path, size)
    except (FileNotFoundError, OSError):
        return pygame.font.Font(None, int(size * 0.8))


def load_spritesheet_icons(png_path="skilltree_spritesheet.png"):
    """Loads icon surfaces using your teammate's Spritesheet class."""
    icons = {}
    try:
        sheet = Spritesheet(png_path)
        icon_mapping = {
            "attack_damage": "01_sword.png",
            "crit_chance": "02_crosshair.png",
            "crit_damage": "03_blazing_star.png",
            "max_health": "11_heart.png",
            "damage_reduction": "12_shield.png",
            "movement_speed": "04_double_chevron.png",
            "shop_expansion": "14_shop.png",
            "purchase_limit": "15_shop_plus.png",
            "blade_damage": "05_dagger.png",
            "ranged_damage": "06_bullet.png",
            "ranged_capacity": "07_triple_bullet.png",
        }
        for skill_id, frame_name in icon_mapping.items():
            icons[skill_id] = sheet.parse_sprite(frame_name)
    except Exception:
        pass
    return icons


class SkillTreeUI:
    NODE_SIZE = 32
    PANEL = pygame.Rect(16, 260, 608, 76)
    BUTTON = pygame.Rect(490, 298, 120, 30)

    def __init__(self, state, base_w=640, base_h=360):
        self.state = state
        self.w, self.h = base_w, base_h
        self.selected = "attack_damage"
        self.message = ""
        self.message_timer = 0
        self.message_color = COL_MUTED

        self.font_title = load_font("fonts/Press_Start_2P/PressStart2P.ttf", 16)
        self.font_name = load_font("fonts/VT323/VT323.ttf", 26)
        self.font = load_font("fonts/VT323/VT323.ttf", 22)
        self.font_small = load_font("fonts/VT323/VT323.ttf", 18)

        # Load icons using Spritesheet class
        self.icons = load_spritesheet_icons()

        # Rectangular node click bounds
        self.node_rects = {}
        half = self.NODE_SIZE // 2
        for skill_id, skill in SKILLS.items():
            cx, cy = skill["pos"]
            self.node_rects[skill_id] = pygame.Rect(cx - half, cy - half, self.NODE_SIZE, self.NODE_SIZE)

    def open(self):
        self.message = ""
        self.message_timer = 0

    def flash_message(self, text, color):
        self.message = text
        self.message_color = color
        self.message_timer = 120

    def handle_event(self, event, mouse_pos=(-1, -1)):
        """Handles mouse clicks and cheat/navigation hotkeys."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.BUTTON.collidepoint(mouse_pos):
                return self.try_buy_selected()

            for skill_id, rect in self.node_rects.items():
                if rect.collidepoint(mouse_pos):
                    self.selected = skill_id
                    self.message = ""
                    return None

        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_k):
                return "close"

            if event.key == pygame.K_F6:
                self.state.add_soul_coins(50)
                self.flash_message("+50 Soul Coins!", COL_SOUL)
                return None

        return None

    def try_buy_selected(self):
        already_owned = self.state.status(self.selected) == "purchased"
        ok, text = self.state.buy(self.selected)
        self.flash_message(text, COL_GOOD if ok else (COL_MUTED if already_owned else COL_BAD))
        return "purchased" if ok else None

    def wrap_text(self, text, font, max_width):
        words = text.split()
        lines = []
        current_line = ""
        for word in words:
            test_line = f"{current_line} {word}".strip()
            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        return lines

    def draw(self, surface, mouse_pos=(-1, -1)):
        if self.message_timer > 0:
            self.message_timer -= 1
            if self.message_timer == 0:
                self.message = ""

        surface.fill(COL_BG)
        pygame.draw.rect(surface, COL_PANEL_BORDER, (0, 0, self.w, self.h), 3)

        self.draw_header(surface)
        self.draw_connections(surface)
        self.draw_hub(surface)
        self.draw_branch_labels(surface)

        for skill_id in SKILLS:
            self.draw_node(surface, skill_id, mouse_pos)

        self.draw_details(surface, mouse_pos)

        hint = self.font_small.render("Mouse: Select / Unlock    ESC / K: Close", False, COL_DIM)
        surface.blit(hint, hint.get_rect(midbottom=(self.w // 2, self.h - 3)))

    def draw_header(self, surface):
        title = self.font_title.render("SKILL TREE", False, COL_TEXT)
        surface.blit(title, (16, 10))

        coins_str = str(self.state.get_coins())
        coins_surf = self.font.render(coins_str, False, COL_SOUL)
        label_surf = self.font_small.render("SOUL COINS", False, COL_MUTED)

        coins_rect = coins_surf.get_rect(topright=(self.w - 16, 10))
        label_rect = label_surf.get_rect(topright=(coins_rect.left - 24, 12))

        surface.blit(coins_surf, coins_rect)
        surface.blit(label_surf, label_rect)
        pygame.draw.circle(surface, COL_SOUL, (coins_rect.left - 12, coins_rect.centery), 6, 2)

    def draw_connections(self, surface):
        for skill_id, skill in SKILLS.items():
            parent = skill["parent"]
            start_pos = HUB_POS if parent is None else SKILLS[parent]["pos"]
            end_pos = skill["pos"]
            branch_col = BRANCHES[skill["branch"]]["color"]
            state = self.state.status(skill_id)

            if state == "purchased":
                pygame.draw.line(surface, branch_col, start_pos, end_pos, 3)
            elif state == "available":
                pygame.draw.line(surface, blend_color(branch_col, COL_BG, 0.5), start_pos, end_pos, 2)
            else:
                pygame.draw.line(surface, (35, 40, 52), start_pos, end_pos, 1)

    def draw_hub(self, surface):
        x, y = HUB_POS
        pygame.draw.rect(surface, COL_PANEL, (x - 12, y - 12, 24, 24))
        pygame.draw.rect(surface, COL_SOUL, (x - 12, y - 12, 24, 24), 2)
        pygame.draw.rect(surface, COL_SOUL, (x - 4, y - 4, 8, 8))

    def draw_branch_labels(self, surface):
        for name, info in BRANCHES.items():
            label = self.font_small.render(name, False, blend_color(info["color"], COL_BG, 0.3))
            surface.blit(label, label.get_rect(center=info["label_pos"]))

    def draw_node(self, surface, skill_id, mouse_pos):
        skill = SKILLS[skill_id]
        rect = self.node_rects[skill_id]
        branch_col = BRANCHES[skill["branch"]]["color"]
        state = self.state.status(skill_id)
        hovered = rect.collidepoint(mouse_pos)

        if state == "purchased":
            fill_col = blend_color(COL_PANEL, branch_col, 0.3)
            border_col = branch_col
        elif state == "available":
            fill_col = COL_PANEL
            border_col = blend_color(branch_col, COL_BG, 0.3)
        else:
            fill_col = (20, 22, 30)
            border_col = (45, 50, 65)

        if hovered and state != "purchased":
            border_col = COL_TEXT

        pygame.draw.rect(surface, fill_col, rect)
        pygame.draw.rect(surface, border_col, rect, 2)

        icon = self.icons.get(skill_id)
        if icon:
            icon_rect = icon.get_rect(center=rect.center)
            surface.blit(icon, icon_rect)

        if skill_id == self.selected:
            phase = (pygame.time.get_ticks() // 150) % 4
            pad = 2 + (phase if phase <= 2 else 4 - phase)
            sel_rect = rect.inflate(pad * 2, pad * 2)
            pygame.draw.rect(surface, COL_TEXT, sel_rect, 1)

    def draw_details(self, surface, mouse_pos):
        skill = SKILLS[self.selected]
        branch_col = BRANCHES[skill["branch"]]["color"]
        state = self.state.status(self.selected)

        pygame.draw.rect(surface, COL_PANEL, self.PANEL)
        pygame.draw.rect(surface, COL_PANEL_BORDER, self.PANEL, 2)
        pygame.draw.rect(surface, branch_col, (self.PANEL.left, self.PANEL.top, 5, self.PANEL.height))

        icon_box = pygame.Rect(self.PANEL.left + 14, self.PANEL.top + 14, 48, 48)
        pygame.draw.rect(surface, (18, 20, 28), icon_box)
        pygame.draw.rect(surface, branch_col if state == "purchased" else COL_PANEL_BORDER, icon_box, 1)
        
        icon = self.icons.get(self.selected)
        if icon:
            surface.blit(icon, icon.get_rect(center=icon_box.center))

        tx = icon_box.right + 14
        title_surf = self.font_name.render(skill["name"], False, COL_TEXT)
        surface.blit(title_surf, (tx, self.PANEL.top + 8))

        tag_surf = self.font_small.render(f"[{skill['branch']}]", False, branch_col)
        surface.blit(tag_surf, (tx + title_surf.get_width() + 10, self.PANEL.top + 13))

        desc_lines = self.wrap_text(skill["desc"], self.font_small, 340)
        if desc_lines:
            desc_surf = self.font_small.render(desc_lines[0], False, COL_MUTED)
            surface.blit(desc_surf, (tx, self.PANEL.top + 34))

        if self.message:
            msg_text, msg_col = self.message, self.message_color
        else:
            msg_text, msg_col = self.state.status_text(self.selected)
        surface.blit(self.font_small.render(msg_text, False, msg_col), (tx, self.PANEL.top + 52))

        cost_col = COL_SOUL if state != "available" or self.state.get_coins() >= skill["cost"] else COL_BAD
        cost_surf = self.font.render(str(skill["cost"]), False, cost_col)
        cost_rect = cost_surf.get_rect(center=(self.BUTTON.centerx + 8, self.PANEL.top + 20))
        surface.blit(cost_surf, cost_rect)
        pygame.draw.circle(surface, cost_col, (cost_rect.left - 10, cost_rect.centery), 5, 2)

        if state == "purchased":
            btn_label, btn_col, btn_bg = "OWNED", COL_GOOD, (20, 40, 25)
        elif state == "available" and self.state.get_coins() >= skill["cost"]:
            hover = self.BUTTON.collidepoint(mouse_pos)
            btn_label = "UNLOCK"
            btn_col = COL_TEXT
            btn_bg = (180, 50, 50) if hover else (120, 35, 35)
        elif state == "available":
            btn_label, btn_col, btn_bg = "NEED COINS", COL_MUTED, (35, 38, 50)
        else:
            btn_label, btn_col, btn_bg = "LOCKED", COL_DIM, (25, 28, 38)

        pygame.draw.rect(surface, btn_bg, self.BUTTON)
        pygame.draw.rect(surface, btn_col, self.BUTTON, 1)
        lbl_surf = self.font_small.render(btn_label, False, btn_col)
        surface.blit(lbl_surf, lbl_surf.get_rect(center=self.BUTTON.center))