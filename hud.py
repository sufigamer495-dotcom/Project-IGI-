from ursina import *

class HUD:
    def __init__(self):
        # Center Crosshair
        self.crosshair = Text(text='+', origin=(0, 0), scale=2, color=color.white)
        self.scope_overlay = Entity(parent=camera.ui, model='quad', scale=(2, 2), color=color.rgba(0, 0, 0, 0.85), enabled=False)
        self.scope_reticle = Text(parent=camera.ui, text='( + )', origin=(0, 0), scale=3, color=color.green, enabled=False)

        # Top Left Stats Panel (Health, Armor, Stamina)
        self.stats_bg = Entity(parent=camera.ui, model='quad', scale=(0.35, 0.18), position=(-0.65, 0.38), color=color.rgba(0, 0, 0, 0.6))

        # Health Bar
        self.health_bar_bg = Entity(parent=camera.ui, model='quad', scale=(0.3, 0.025), position=(-0.65, 0.43), color=color.dark_gray)
        self.health_bar = Entity(parent=camera.ui, model='quad', scale=(0.3, 0.025), position=(-0.65, 0.43), color=color.red, origin=(-0.5, 0))
        self.health_text = Text(parent=camera.ui, text='HP: 100', position=(-0.8, 0.43), scale=0.8, color=color.white)
        self.health_bar.x = -0.8  # Left aligned relative to container

        # Armor Bar
        self.armor_bar_bg = Entity(parent=camera.ui, model='quad', scale=(0.3, 0.025), position=(-0.65, 0.39), color=color.dark_gray)
        self.armor_bar = Entity(parent=camera.ui, model='quad', scale=(0.3, 0.025), position=(-0.65, 0.39), color=color.azure, origin=(-0.5, 0))
        self.armor_text = Text(parent=camera.ui, text='AP: 100', position=(-0.8, 0.39), scale=0.8, color=color.white)
        self.armor_bar.x = -0.8

        # Stamina Bar
        self.stamina_bar_bg = Entity(parent=camera.ui, model='quad', scale=(0.3, 0.025), position=(-0.65, 0.35), color=color.dark_gray)
        self.stamina_bar = Entity(parent=camera.ui, model='quad', scale=(0.3, 0.025), position=(-0.65, 0.35), color=color.yellow, origin=(-0.5, 0))
        self.stamina_text = Text(parent=camera.ui, text='STM: 100%', position=(-0.8, 0.35), scale=0.8, color=color.white)
        self.stamina_bar.x = -0.8

        # Top Right Mission / Weather / Alert Status Panel
        self.info_bg = Entity(parent=camera.ui, model='quad', scale=(0.45, 0.22), position=(0.6, 0.36), color=color.rgba(0, 0, 0, 0.6))
        self.level_text = Text(parent=camera.ui, text='Level: 1 - Mission Title', position=(0.4, 0.44), scale=0.9, color=color.cyan)
        self.objective_text = Text(parent=camera.ui, text='Objective: HACK TERMINAL', position=(0.4, 0.40), scale=0.8, color=color.yellow)
        self.season_text = Text(parent=camera.ui, text='Season: Winter', position=(0.4, 0.36), scale=0.8, color=color.white)
        self.alert_text = Text(parent=camera.ui, text='Status: Clear Patrol', position=(0.4, 0.32), scale=0.8, color=color.green)

        # Bottom Right Weapon & Ammo Display
        self.weapon_bg = Entity(parent=camera.ui, model='quad', scale=(0.35, 0.12), position=(0.65, -0.4), color=color.rgba(0, 0, 0, 0.6))
        self.weapon_text = Text(parent=camera.ui, text='Weapon: Suppressed Pistol', position=(0.5, -0.37), scale=0.8, color=color.white)
        self.ammo_text = Text(parent=camera.ui, text='Ammo: 12 / 48', position=(0.5, -0.41), scale=1.0, color=color.orange)

        # Center Interaction Prompt
        self.prompt_text = Text(parent=camera.ui, text='', origin=(0, 0), position=(0, -0.2), scale=1.2, color=color.yellow)

    def update_stats(self, health, max_health, armor, max_armor, stamina, max_stamina):
        h_ratio = max(0.0, health / max_health)
        a_ratio = max(0.0, armor / max_armor)
        s_ratio = max(0.0, stamina / max_stamina)

        self.health_bar.scale_x = 0.3 * h_ratio
        self.health_text.text = f'HP: {int(health)}'

        self.armor_bar.scale_x = 0.3 * a_ratio
        self.armor_text.text = f'AP: {int(armor)}'

        self.stamina_bar.scale_x = 0.3 * s_ratio
        self.stamina_text.text = f'STM: {int(stamina)}%'

    def update_mission_info(self, level_name, objective, season, alert_status):
        self.level_text.text = f'Level: {level_name}'
        self.objective_text.text = f'Objective: {objective}'
        self.season_text.text = f'Season: {season}'
        self.alert_text.text = f'Status: {alert_status}'

        if alert_status == 'Clear Patrol':
            self.alert_text.color = color.green
        elif alert_status == 'Caution':
            self.alert_text.color = color.yellow
        else:
            self.alert_text.color = color.red

    def update_weapon_info(self, weapon_name, current_clip, reserve_ammo, is_reloading):
        self.weapon_text.text = f'Weapon: {weapon_name}'
        if is_reloading:
            self.ammo_text.text = 'RELOADING...'
            self.ammo_text.color = color.yellow
        else:
            self.ammo_text.text = f'Ammo: {current_clip} / {reserve_ammo}'
            self.ammo_text.color = color.orange if current_clip > 0 else color.red

    def set_prompt(self, text):
        self.prompt_text.text = text

    def set_scoped(self, scoped):
        self.crosshair.enabled = not scoped
        self.scope_overlay.enabled = scoped
        self.scope_reticle.enabled = scoped
