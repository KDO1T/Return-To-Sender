import math

import pygame

COL_BG = (12, 12, 16)
COL_PANEL = (20, 20, 26)
COL_PANEL_BORDER = (60, 60, 70)
COL_TEXT = (240, 240, 240)
COL_MUTED = (140, 140, 140)
COL_DIM = (70, 70, 80)
COL_ACCENT = (235, 65, 40)
COL_SOUL = (100, 230, 220)
COL_BAD = (235, 65, 40)
COL_GOOD = (110, 215, 110)

HUB_POS = (320, 160) # position for the center of the skill tree

BRANCHES = {
    "COMBAT":   {"color": (235, 65, 40),   "label_pos": (200, 44)},
    "SURVIVAL": {"color": (90, 200, 90),   "label_pos": (213, 222)},
    "MOVEMENT": {"color": (80, 170, 235),  "label_pos": (320, 252)},
    "ECONOMY":  {"color": (235, 190, 60),  "label_pos": (400, 222)},
    "WEAPONS":  {"color": (175, 115, 235), "label_pos": (440, 44)},
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
    "attack_speed": {
        "name": "Attack Speed", "branch": "COMBAT", "cost": 15, "pos": (268, 80),
        "parent": "attack_damage", "requires_ranged": False,
        "desc": "Attack 15% faster between hits.",
        "effects": {"attack_speed_pct": 0.15},
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
    "knockback_resistance": {
        "name": "Knockback Resistance", "branch": "SURVIVAL", "cost": 20, "pos": (158, 195),
        "parent": "damage_reduction", "requires_ranged": False,
        "desc": "Reduces the knockback you take by 50%.",
        "effects": {"knockback_resist": 0.50},
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
    "blade_attack_speed": {
        "name": "Blade Attack Speed", "branch": "WEAPONS", "cost": 16, "pos": (427, 125),
        "parent": "blade_damage", "requires_ranged": False,
        "desc": "Blade swings 15% faster.",
        "effects": {"attack_speed_pct": 0.15},
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
    "damage_pct", "crit_chance", "crit_damage", "attack_speed_pct", "max_hp",
    "damage_reduction", "knockback_resist", "move_speed_bonus", "shop_slots",
    "purchase_limit", "ranged_damage_pct", "ranged_capacity",
)

MIN_COMBO_COOLDOWN = 6      # limit the attack speed so it can never push the combo delay below 6 frames


# state of skill tree
class SkillTreeState:

    def __init__(self, player):
        self.player = player

        saved = getattr(player, "skill_tree_purchased", None) or []
        clean = []
        # ignores duplocates in old save
        for skill_id in saved:
            if skill_id in SKILLS and skill_id not in clean:
                clean.append(skill_id)
        player.skill_tree_purchased = clean

        if not hasattr(player, "ranged_unlocked"):
            player.ranged_unlocked = False

    @property
    def purchased(self):
        return self.player.skill_tree_purchased

    @property
    def coins(self):
        return int(self.player.S_COIN or 0)

    @property
    def ranged_unlocked(self):
        return bool(getattr(self.player, "ranged_unlocked", False))

    def unlock_ranged_weapon(self):
        """Call this when the final boss is defeated."""
        self.player.ranged_unlocked = True

    def status(self, skill_id):
        """'purchased' | 'available' | 'locked' | 'sealed'"""
        skill = SKILLS[skill_id]
        if skill_id in self.purchased:
            return "purchased"
        if skill["requires_ranged"] and not self.ranged_unlocked:
            return "sealed"
        parent = skill["parent"]
        if parent is not None and parent not in self.purchased:
            return "locked"
        return "available"

    def status_text(self, skill_id):
        """Human readable line for the detail panel -> (text, colour)."""
        state = self.status(skill_id)
        skill = SKILLS[skill_id]
        if state == "purchased":
            return "UNLOCKED", COL_GOOD
        if state == "sealed":
            return "SEALED - Unlocks after the final boss", BRANCHES["WEAPONS"]["color"]
        if state == "locked":
            return f"LOCKED - Requires {SKILLS[skill['parent']]['name']}", COL_MUTED
        if self.coins < skill["cost"]:
            return f"AVAILABLE - Need {skill['cost'] - self.coins} more coins", COL_ACCENT
        return "AVAILABLE", (235, 190, 60)

    def can_buy(self, skill_id):
        return self.status(skill_id) == "available" and self.coins >= SKILLS[skill_id]["cost"]

    # --------------- actions ------------------------------------------------------------------
    def buy(self, skill_id):
        """Returns (success, message)."""
        state = self.status(skill_id)
        skill = SKILLS[skill_id]

        if state == "purchased":
            return False, "Already unlocked."
        if state == "sealed":
            return False, "Defeat the final boss first."
        if state == "locked":
            return False, f"Unlock {SKILLS[skill['parent']]['name']} first."
        if self.coins < skill["cost"]:
            return False, "Not enough Soul Coins."

        self.player.S_COIN = self.coins - skill["cost"]
        self.purchased.append(skill_id)
        return True, f"{skill['name']} unlocked!"

    # ---- effects ------------------------------------------------------------------
    def effects(self):
        """Sum of every purchased skill's effects (all keys always present)."""
        totals = {key: 0 for key in EFFECT_KEYS}
        for skill_id in self.purchased:
            for key, value in SKILLS[skill_id]["effects"].items():
                totals[key] += value
        return totals


def apply_skill_effects(player, tree, heal_on_gain=True):
    """
    Copies the skill-tree bonuses onto the player. Safe to call as many times as you like
    (it removes the previous max-HP bonus before adding the new one).

    heal_on_gain=True  -> when Maximum Health is bought, current HP also goes up by the same amount
    heal_on_gain=False -> use right after loading a save so HP is not changed
    """
    fx = tree.effects()

    # max HP
    old_bonus = getattr(player, "bonus_max_HP", 0)
    new_bonus = int(fx["max_hp"])
    delta = new_bonus - old_bonus
    player.max_HP += delta
    if heal_on_gain and delta > 0:
        player.HP += delta
    player.HP = min(player.HP, player.max_HP)
    player.bonus_max_HP = new_bonus

    # combat
    player.damage_mult = 1.0 + fx["damage_pct"]
    player.crit_chance_bonus = fx["crit_chance"]
    player.crit_dmg_bonus = fx["crit_damage"]

    base_cd = getattr(player, "base_combo_cooldown", player.combo_cooldown)
    player.combo_cooldown = max(MIN_COMBO_COOLDOWN, round(base_cd / (1.0 + fx["attack_speed_pct"])))

    # survival
    player.damage_reduction = min(0.9, fx["damage_reduction"])
    player.knockback_resist = min(1.0, fx["knockback_resist"])

    # movement (base speed 4 px/frame; Rect positions are integers so the bonus is whole pixels)
    player.move_speed = getattr(player, "base_move_speed", 4) + int(fx["move_speed_bonus"])

    # values for systems that do not exist yet (like the shop and the ranged weapon) just change from here later
    player.skill_effects = fx

# rendering for icons
def _p(cx, cy, k, x, y):
    return (int(round(cx + x * k)), int(round(cy + y * k)))


def _bullet(surf, cx, cy, k, col, ox=0.0, scale=1.0):
    s = k * scale
    x = cx + ox * k
    pygame.draw.rect(surf, col, (int(x - 3 * s), int(cy - 2 * s), max(1, int(6 * s)), max(1, int(10 * s))))
    pygame.draw.polygon(surf, col, [(int(x - 3 * s), int(cy - 2 * s)), (int(x), int(cy - 8 * s)), (int(x + 3 * s), int(cy - 2 * s))])
    pygame.draw.line(surf, COL_BG, (int(x - 3 * s), int(cy + 5 * s)), (int(x + 3 * s), int(cy + 5 * s)), max(1, int(s)))


def draw_icon(surf, skill_id, cx, cy, col, k=1.0):
    w = max(1, int(round(2 * k)))
    P = lambda x, y: _p(cx, cy, k, x, y)


    if skill_id == "attack_damage":
        pygame.draw.line(surf, col, P(-4, 4), P(6, -6), max(2, int(3 * k)))
        pygame.draw.line(surf, col, P(-6, 0), P(0, 6), w)
        pygame.draw.circle(surf, col, P(-7, 7), max(1, int(1.5 * k)))

    elif skill_id == "crit_chance":
        pygame.draw.circle(surf, col, P(0, 0), int(6 * k), w)
        for a, b in (((-9, 0), (-3, 0)), ((3, 0), (9, 0)), ((0, -9), (0, -3)), ((0, 3), (0, 9))):
            pygame.draw.line(surf, col, P(*a), P(*b), w)
        pygame.draw.circle(surf, col, P(0, 0), max(1, int(1.2 * k)))


    elif skill_id == "crit_damage":
        pts = []
        for i in range(16):
            r = 9 if i % 2 == 0 else 3.6
            ang = math.pi * i / 8 - math.pi / 2
            pts.append(P(math.cos(ang) * r, math.sin(ang) * r))
        pygame.draw.polygon(surf, col, pts)

    elif skill_id in ("attack_speed",):
        pygame.draw.lines(surf, col, False, [P(-8, -6), P(-2, 0), P(-8, 6)], w)
        pygame.draw.lines(surf, col, False, [P(0, -6), P(6, 0), P(0, 6)], w)

    elif skill_id == "max_health":
        pygame.draw.circle(surf, col, P(-3.5, -2), int(4.2 * k))
        pygame.draw.circle(surf, col, P(3.5, -2), int(4.2 * k))
        pygame.draw.polygon(surf, col, [P(-7.6, 0), P(7.6, 0), P(0, 8.5)])

    elif skill_id == "damage_reduction":
        pts = [P(-7, -7), P(7, -7), P(7, 1), P(0, 8), P(-7, 1)]
        pygame.draw.polygon(surf, col, pts, w)
        pygame.draw.line(surf, col, P(0, -7), P(0, 7), max(1, int(k)))

    elif skill_id == "knockback_resistance":
        pygame.draw.rect(surf, col, (int(cx + 2 * k), int(cy - 8 * k), max(2, int(5 * k)), max(2, int(16 * k))))
        pygame.draw.line(surf, col, P(-8, 0), P(-1, 0), w)
        pygame.draw.polygon(surf, col, [P(-3, -3), P(0, 0), P(-3, 3)])

    elif skill_id == "movement_speed":
        pygame.draw.line(surf, col, P(-8, -4), P(-3, -4), w)
        pygame.draw.line(surf, col, P(-8, 4), P(-3, 4), w)
        pygame.draw.line(surf, col, P(-6, 0), P(2, 0), w)
        pygame.draw.polygon(surf, col, [P(1, -6), P(8, 0), P(1, 6)])

    elif skill_id == "shop_expansion":
        pygame.draw.polygon(surf, col, [P(-8, -2), P(-6, -8), P(6, -8), P(8, -2)])
        pygame.draw.rect(surf, col, (int(cx - 6 * k), int(cy - 2 * k), max(2, int(12 * k)), max(2, int(10 * k))), w)
        pygame.draw.rect(surf, col, (int(cx - 2 * k), int(cy + 2 * k), max(2, int(4 * k)), max(2, int(6 * k))))

    elif skill_id == "purchase_limit":
        for y in (-7, -2, 3):
            pygame.draw.ellipse(surf, col, (int(cx - 6 * k), int(cy + y * k), max(2, int(12 * k)), max(2, int(5 * k))), max(1, int(k)))



    elif skill_id == "blade_damage":
        pygame.draw.polygon(surf, col, [P(0, -9), P(2, -6), P(2, 3), P(-2, 3), P(-2, -6)])
        pygame.draw.rect(surf, col, (int(cx - 5 * k), int(cy + 3 * k), max(2, int(10 * k)), max(1, int(2 * k))))
        pygame.draw.rect(surf, col, (int(cx - 1 * k), int(cy + 5 * k), max(1, int(2 * k)), max(2, int(3 * k))))
        pygame.draw.circle(surf, col, P(0, 9), max(1, int(1.3 * k)))


    elif skill_id == "blade_attack_speed":
        pygame.draw.polygon(surf, col, [P(4, -9), P(6, -6), P(6, 3), P(2, 3), P(2, -6)])
        pygame.draw.rect(surf, col, (int(cx - 1 * k), int(cy + 3 * k), max(2, int(10 * k)), max(1, int(2 * k))))
        pygame.draw.rect(surf, col, (int(cx + 3 * k), int(cy + 5 * k), max(1, int(2 * k)), max(2, int(3 * k))))
        for y, x0 in ((-6, -9), (-2, -8), (2, -9)):
            pygame.draw.line(surf, col, P(x0, y), P(-2, y), max(1, int(k)))

    elif skill_id == "ranged_damage":                       
        _bullet(surf, cx, cy, k, col)

    elif skill_id == "ranged_capacity":                     
        for ox in (-6, 0, 6):
            _bullet(surf, cx, cy + 1 * k, k, col, ox, 0.8)


def _draw_padlock(surf, x, y, col):
    """Tiny padlock, (x, y) = top-left of a 7x9 area."""
    pygame.draw.rect(surf, col, (x + 1, y, 5, 5), 1)
    pygame.draw.rect(surf, col, (x, y + 4, 7, 5))


def _draw_check(surf, x, y, col):
    pygame.draw.lines(surf, col, False, [(x, y + 3), (x + 2, y + 5), (x + 6, y)], 2)


def _blend(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def _load_font(path, size):
    try:
        return pygame.font.Font(path, size)
    except (FileNotFoundError, OSError):
        return pygame.font.Font(None, int(size * 0.8))



#--------- UI--------------------------------------------------------------

class SkillTreeUI:
    NODE = 32
    PANEL = pygame.Rect(16, 264, 608, 76)       # detail panel
    BUTTON = pygame.Rect(494, 296, 120, 28)     # unlock button

    def __init__(self, state, base_w=640, base_h=360):
        self.state = state
        self.w, self.h = base_w, base_h
        self.selected = "attack_damage"
        self.message = ""
        self.message_timer = 0
        self.message_color = COL_MUTED

        self.font_title = _load_font("fonts/Press_Start_2P/PressStart2P.ttf", 16)
        self.font_name = _load_font("fonts/VT323/VT323.ttf", 30)
        self.font = _load_font("fonts/VT323/VT323.ttf", 24)
        self.font_small = _load_font("fonts/VT323/VT323.ttf", 20)

        self.node_rects = {
            skill_id: pygame.Rect(0, 0, self.NODE, self.NODE) for skill_id in SKILLS
        }
        for skill_id, rect in self.node_rects.items():
            rect.center = SKILLS[skill_id]["pos"]

        self.background = self._build_background()

    # initialize and reset the UI
    def _build_background(self):
        bg = pygame.Surface((self.w, self.h))
        bg.fill(COL_BG)
        for x in range(8, self.w, 16):
            for y in range(40, 262, 16):
                bg.set_at((x, y), (24, 24, 30))
        vignette = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        for i in range(28):                                     # dark edges
            alpha = int(150 * (1 - i / 28) ** 2)
            pygame.draw.rect(vignette, (0, 0, 0, alpha), (i, i, self.w - 2 * i, self.h - 2 * i), 1)
        bg.blit(vignette, (0, 0))
        pygame.draw.line(bg, COL_PANEL_BORDER, (0, 31), (self.w, 31), 2)
        return bg

    def open(self):
        self.message = ""
        self.message_timer = 0

    def _flash(self, text, color):
        self.message = text
        self.message_color = color
        self.message_timer = 100

    # input
    def handle_event(self, event, mouse_pos):
        """
        mouse_pos: mouse position already converted to 640x360 canvas coordinates.
        Returns None, "close" or "purchased".
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.BUTTON.collidepoint(mouse_pos):
                return self._try_buy()
            for skill_id, rect in self.node_rects.items():
                if rect.inflate(6, 6).collidepoint(mouse_pos):
                    self.selected = skill_id
                    self.message = ""
                    return None

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_k:
                return "close"
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_e):
                return self._try_buy()
            direction = {
                pygame.K_LEFT: (-1, 0), pygame.K_a: (-1, 0),
                pygame.K_RIGHT: (1, 0), pygame.K_d: (1, 0),
                pygame.K_UP: (0, -1), pygame.K_w: (0, -1),
                pygame.K_DOWN: (0, 1), pygame.K_s: (0, 1),
            }.get(event.key)
            if direction:
                self._move_selection(direction)
        return None

    def _try_buy(self):
        already_owned = self.state.status(self.selected) == "purchased"
        ok, text = self.state.buy(self.selected)
        self._flash(text, COL_GOOD if ok else (COL_MUTED if already_owned else COL_BAD))
        return "purchased" if ok else None

    def _move_selection(self, direction):
        sx, sy = SKILLS[self.selected]["pos"]
        best, best_score = None, None
        for skill_id, skill in SKILLS.items():
            if skill_id == self.selected:
                continue
            dx, dy = skill["pos"][0] - sx, skill["pos"][1] - sy
            along = dx * direction[0] + dy * direction[1]       # distance in the pressed direction
            across = abs(dx * direction[1]) + abs(dy * direction[0])
            if along <= 4:
                continue
            score = along + across * 2
            if best_score is None or score < best_score:
                best, best_score = skill_id, score
        if best:
            self.selected = best
            self.message = ""

    # -------------------------------------- drawing --------------------------------------------
    def draw(self, surface, mouse_pos=(-1, -1)):
        if self.message_timer > 0:
            self.message_timer -= 1
            if self.message_timer == 0:
                self.message = ""

        surface.blit(self.background, (0, 0))
        self._draw_header(surface)
        self._draw_connections(surface)
        self._draw_hub(surface)
        self._draw_branch_labels(surface)
        for skill_id in SKILLS:
            self._draw_node(surface, skill_id, mouse_pos)
        self._draw_details(surface, mouse_pos)

        hint = self.font_small.render(
            "Click / Arrows: select    Enter: unlock    ESC / K: close", False, COL_DIM)
        surface.blit(hint, hint.get_rect(midbottom=(self.w // 2, self.h - 3)))

    def _draw_header(self, surface):
        title = self.font_title.render("SKILL TREE", False, COL_TEXT)
        surface.blit(title, title.get_rect(midleft=(16, 16)))

        coins = self.font.render(f"{self.state.coins}", False, COL_SOUL)
        label = self.font_small.render("SOUL COINS", False, COL_MUTED)
        coin_rect = coins.get_rect(midright=(self.w - 16, 16))
        label_rect = label.get_rect(midright=(coin_rect.left - 26, 16))
        surface.blit(coins, coin_rect)
        surface.blit(label, label_rect)
        self._draw_coin(surface, coin_rect.left - 13, 16, 7)

    def _draw_coin(self, surface, x, y, r):
        pygame.draw.circle(surface, _blend(COL_SOUL, (0, 0, 0), 0.55), (x, y), r)
        pygame.draw.circle(surface, COL_SOUL, (x, y), r, 2)
        pygame.draw.circle(surface, COL_SOUL, (x, y), max(1, r // 3))

    def _draw_connections(self, surface):
        for skill_id, skill in SKILLS.items():
            parent = skill["parent"]
            start = HUB_POS if parent is None else SKILLS[parent]["pos"]
            end = skill["pos"]
            base = BRANCHES[skill["branch"]]["color"]
            state = self.state.status(skill_id)

            if state == "purchased":
                pygame.draw.line(surface, _blend(base, (0, 0, 0), 0.5), start, end, 5)   # glow
                pygame.draw.line(surface, base, start, end, 3)
            elif state == "available":
                pygame.draw.line(surface, _blend(base, COL_BG, 0.6), start, end, 2)
            else:
                pygame.draw.line(surface, (36, 36, 44), start, end, 2)

    def _draw_hub(self, surface):
        x, y = HUB_POS
        pulse = 0.5 + 0.5 * math.sin(pygame.time.get_ticks() / 500)
        pygame.draw.circle(surface, _blend(COL_BG, COL_SOUL, 0.10 + 0.08 * pulse), (x, y), 19)
        pygame.draw.circle(surface, COL_PANEL, (x, y), 14)
        pygame.draw.circle(surface, _blend(COL_MUTED, COL_SOUL, 0.5), (x, y), 14, 2)
        pygame.draw.polygon(surface, COL_SOUL, [(x, y - 7), (x + 5, y), (x, y + 7), (x - 5, y)])

    def _draw_branch_labels(self, surface):
        for name, info in BRANCHES.items():
            text = self.font_small.render(name, False, _blend(info["color"], COL_BG, 0.25))
            surface.blit(text, text.get_rect(center=info["label_pos"]))

    def _draw_node(self, surface, skill_id, mouse_pos):
        skill = SKILLS[skill_id]
        rect = self.node_rects[skill_id]
        base = BRANCHES[skill["branch"]]["color"]
        state = self.state.status(skill_id)
        hovered = rect.collidepoint(mouse_pos)

        if state == "purchased":
            fill = _blend(COL_PANEL, base, 0.28)
            border = base
            icon = _blend(base, (255, 255, 255), 0.35)
        elif state == "available":
            fill = _blend(COL_PANEL, base, 0.08)
            border = _blend(base, COL_BG, 0.35)
            icon = _blend(base, COL_TEXT, 0.35)
        else:
            fill = (16, 16, 20)
            border = (44, 44, 52)
            icon = (58, 58, 66)

        if hovered and state != "purchased":
            border = _blend(border, COL_TEXT, 0.35)

        if state == "purchased":
            glow = rect.inflate(6, 6)
            pygame.draw.rect(surface, _blend(COL_BG, base, 0.25), glow)

        pygame.draw.rect(surface, fill, rect)
        pygame.draw.rect(surface, border, rect, 2)
        draw_icon(surface, skill_id, rect.centerx, rect.centery, icon, 1.0)

        if state == "purchased":
            _draw_check(surface, rect.right - 9, rect.top + 3, COL_TEXT)
        elif state in ("locked", "sealed"):
            pad_col = BRANCHES["WEAPONS"]["color"] if state == "sealed" else (95, 95, 105)
            _draw_padlock(surface, rect.right - 9, rect.bottom - 11, pad_col)

        if skill_id == self.selected:
            t = pygame.time.get_ticks() / 250
            pad = 4 + int(1.5 * (0.5 + 0.5 * math.sin(t)))
            sel = rect.inflate(pad * 2, pad * 2)
            c, L = COL_TEXT, 6
            for (px, py, sx, sy) in ((sel.left, sel.top, 1, 1), (sel.right - 1, sel.top, -1, 1),
                                     (sel.left, sel.bottom - 1, 1, -1), (sel.right - 1, sel.bottom - 1, -1, -1)):
                pygame.draw.line(surface, c, (px, py), (px + sx * L, py), 2)
                pygame.draw.line(surface, c, (px, py), (px, py + sy * L), 2)

    def _draw_details(self, surface, mouse_pos):
        skill = SKILLS[self.selected]
        base = BRANCHES[skill["branch"]]["color"]
        state = self.state.status(self.selected)

        panel = self.PANEL
        pygame.draw.rect(surface, COL_PANEL, panel)
        pygame.draw.rect(surface, COL_PANEL_BORDER, panel, 2)
        pygame.draw.line(surface, base, (panel.left + 2, panel.top + 1), (panel.right - 3, panel.top + 1), 2)

        # big icon box
        box = pygame.Rect(panel.left + 12, panel.top + 12, 52, 52)
        active = state in ("purchased", "available")
        pygame.draw.rect(surface, _blend(COL_BG, base, 0.15) if active else (16, 16, 20), box)
        pygame.draw.rect(surface, base if state == "purchased" else (_blend(base, COL_BG, 0.4) if active else (44, 44, 52)), box, 2)
        draw_icon(surface, self.selected, box.centerx, box.centery,
                  _blend(base, COL_TEXT, 0.3) if active else (70, 70, 78), 2.2)

        tx = box.right + 14
        name = self.font_name.render(skill["name"], False, COL_TEXT)
        surface.blit(name, (tx, panel.top + 4))
        tag = self.font_small.render(f"[ {skill['branch']} ]", False, base)
        surface.blit(tag, tag.get_rect(midleft=(tx + name.get_width() + 10, panel.top + 17)))

        # description (wrapped to the space left of the cost / button column)
        for i, line in enumerate(self._wrap(skill["desc"], self.font, 390)[:1]):
            surface.blit(self.font.render(line, False, (200, 200, 205)), (tx, panel.top + 30 + i * 16))

        # temporary feedback message
        if self.message:
            status_text, status_color = self.message, self.message_color
        else:
            status_text, status_color = self.state.status_text(self.selected)
        surface.blit(self.font_small.render(status_text, False, status_color), (tx, panel.bottom - 22))

        # cost and unlock button
        cost_col = COL_SOUL
        if state in ("available",) and self.state.coins < skill["cost"]:
            cost_col = COL_BAD
        cost = self.font_name.render(str(skill["cost"]), False, cost_col)
        cost_rect = cost.get_rect(midleft=(self.BUTTON.centerx - 8, panel.top + 20))
        surface.blit(cost, cost_rect)
        self._draw_coin(surface, cost_rect.left - 12, cost_rect.centery, 7)

        if state == "purchased":
            label, label_col, edge, fill = "OWNED", COL_GOOD, (60, 110, 60), (18, 30, 18)
        elif state == "available" and self.state.coins >= skill["cost"]:
            hover = self.BUTTON.collidepoint(mouse_pos)
            label, label_col = "UNLOCK", COL_TEXT
            edge = COL_TEXT if hover else COL_ACCENT
            fill = (70, 22, 14) if hover else (45, 16, 12)
        elif state == "available":
            label, label_col, edge, fill = "NEED COINS", COL_MUTED, (70, 70, 80), (20, 20, 26)
        else:
            label, label_col, edge, fill = "LOCKED", COL_DIM, (50, 50, 58), (16, 16, 20)
        pygame.draw.rect(surface, fill, self.BUTTON)
        pygame.draw.rect(surface, edge, self.BUTTON, 2)
        text = self.font.render(label, False, label_col)
        surface.blit(text, text.get_rect(center=self.BUTTON.center))

    @staticmethod
    def _wrap(text, font, max_width):
        words, lines, line = text.split(), [], ""
        for word in words:
            trial = f"{line} {word}".strip()
            if font.size(trial)[0] <= max_width:
                line = trial
            else:
                lines.append(line)
                line = word
        if line:
            lines.append(line)
        return lines
