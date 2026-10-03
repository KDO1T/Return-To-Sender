import pygame


def draw_hud(surface, player, zombies, camera_x, camera_y, screen_w, screen_h, stage_kill_count, font, font_small, dash_icon):

    # Bottom Left
    hp_bar_width = 200
    hp_bar_height = 20
    hp_x = 20
    hp_y = screen_h - hp_bar_height - 20
    

    health_ratio = max(0, player.HP / player.max_HP)
    current_hp_width = int(hp_bar_width * health_ratio)
    
    pygame.draw.rect(surface, (40, 40, 40), (hp_x, hp_y, hp_bar_width, hp_bar_height))
    pygame.draw.rect(surface, (50, 205, 50), (hp_x, hp_y, current_hp_width, hp_bar_height))
    pygame.draw.rect(surface, (200, 200, 200), (hp_x, hp_y, hp_bar_width, hp_bar_height), 2) # Border

    # Dash Charges
    dash_icon_y = hp_y - dash_icon.get_height() - 5
    icon_width = dash_icon.get_width()

    dimmed_dash_icon = dash_icon.copy()
    dimmed_dash_icon.set_alpha(70)

    for i in range(player.max_dash_charges):
        icon_x = hp_x + 5 + (i * (icon_width + 5))

        if i < player.dash_charges:
            surface.blit(dash_icon, (icon_x, dash_icon_y))
        else:
            surface.blit(dimmed_dash_icon, (icon_x, dash_icon_y))


    # Bottom Right
    hit_text = font.render(f"Hits: {player.hit_number}", True, (255, 255, 255))
    combo_text = font.render(f"Combo: {player.combo_stage}x", True, (255, 215, 0))
    
    hit_rect = hit_text.get_rect(bottomright=(screen_w - 20, screen_h - 40))
    combo_rect = combo_text.get_rect(bottomright=(screen_w - 20, screen_h - 15))
    
    surface.blit(hit_text, hit_rect)
    surface.blit(combo_text, combo_rect)

    # Top Right
    coins_text = font.render(f"Soul Coins: {player.S_COIN or 0}", True, (180, 100, 255))
    dollars_text = font.render(f"Dollars: ${player.DOLLARS or 0}", True, (50, 205, 50))
    kills_text = font_small.render(f"Stage Kills: {stage_kill_count}", True, (150, 150, 150))
    
    coins_rect = coins_text.get_rect(topright=(screen_w - 20, 20))
    dollars_rect = dollars_text.get_rect(topright=(screen_w - 20, coins_rect.bottom + 5))
    kills_rect = kills_text.get_rect(topright=(screen_w - 20, dollars_rect.bottom + 5))
    
    surface.blit(coins_text, coins_rect)
    surface.blit(dollars_text, dollars_rect)
    surface.blit(kills_text, kills_rect)

    # Hp bar above zombies
    zombie_hp_width = 30
    zombie_hp_height = 5

    for zombie in zombies:
        if not hasattr(zombie, 'max_HP'):
            zombie.max_HP = getattr(zombie, 'max_hp', getattr(zombie, 'max_health', zombie.HP))

        z_max_hp = zombie.max_HP
        
        if z_max_hp > 0 and zombie.HP > 0:
            z_health_pct = zombie.HP / z_max_hp
            
            if z_health_pct > 0.75:
                bar_color = (50, 205, 50)   # Green
            elif z_health_pct > 0.50:
                bar_color = (255, 215, 0)   # Yellow
            elif z_health_pct > 0.25:
                bar_color = (255, 140, 0)   # Orange
            else:
                bar_color = (220, 20, 60)   # Red

            current_z_width = int(zombie_hp_width * z_health_pct)
            
            render_x = zombie.rect.centerx - camera_x - (zombie_hp_width // 2)
            render_y = zombie.rect.top - camera_y - 15

            pygame.draw.rect(surface, (40, 40, 40), (render_x, render_y, zombie_hp_width, zombie_hp_height))
            pygame.draw.rect(surface, bar_color, (render_x, render_y, current_z_width, zombie_hp_height))
            pygame.draw.rect(surface, (0, 0, 0), (render_x, render_y, zombie_hp_width, zombie_hp_height), 1)