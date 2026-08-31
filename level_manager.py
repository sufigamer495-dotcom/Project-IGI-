import json
import os
import random
from ursina import *
from enemy import Enemy

COLOR_MAP = {
    'gray': color.gray,
    'dark_gray': color.dark_gray,
    'olive': color.rgb(80, 100, 50),
    'black': color.black,
    'white': color.white,
    'khaki': color.rgb(190, 180, 110),
    'brown': color.brown
}

class LevelManager:
    def __init__(self, weather_manager=None, json_path="levels.json"):
        self.weather_manager = weather_manager
        self.json_path = json_path
        self.levels_data = self.load_levels_data()
        self.current_level_idx = 0
        self.current_level_data = None

        # Level objects container
        self.level_entities = []
        self.enemies = []
        self.objective_entity = None
        self.objective_completed = False
        self.target_enemy = None

        # World Ground & Sky
        self.ground = Entity(model='plane', scale=(150, 1, 150), color=color.gray, collider='box')
        self.sky = Sky()

        if self.weather_manager:
            self.weather_manager.ground = self.ground
            self.weather_manager.sky = self.sky

    def load_levels_data(self):
        if not os.path.exists(self.json_path):
            raise FileNotFoundError(f"Levels JSON file not found at {self.json_path}")
        with open(self.json_path, 'r') as f:
            return json.load(f)

    def load_level(self, level_num, player=None):
        idx = level_num - 1
        if idx < 0 or idx >= len(self.levels_data):
            print(f"Level index {idx} out of range!")
            return False

        self.current_level_idx = idx
        self.current_level_data = self.levels_data[idx]
        self.objective_completed = False

        # Clear existing entities
        self.clear_level()

        # Update Weather Season
        season = self.current_level_data.get('season', 'Winter')
        if self.weather_manager:
            self.weather_manager.set_season(season)

        # Reposition Player
        spawn_pos = Vec3(*self.current_level_data.get('player_spawn', [0, 1, -20]))
        if player:
            player.position = spawn_pos

        # Generate Map Structures
        self.generate_structures()

        # Generate Terrain Trees
        self.generate_trees()

        # Generate Objective Entity / Terminal / Target
        self.generate_objective()

        # Spawn Enemies
        self.spawn_enemies(player)

        return True

    def clear_level(self):
        for e in self.level_entities:
            destroy(e)
        self.level_entities.clear()

        for en in self.enemies:
            destroy(en)
        self.enemies.clear()

        if self.objective_entity:
            destroy(self.objective_entity)
            self.objective_entity = None

    def generate_structures(self):
        structures = self.current_level_data.get('structures', [])
        for struct_info in structures:
            stype = struct_info.get('type')
            pos = Vec3(*struct_info.get('pos', [0, 0, 0]))
            s_scale = Vec3(*struct_info.get('scale', [2, 2, 2]))
            c_name = struct_info.get('color', 'gray')
            col = COLOR_MAP.get(c_name, color.gray)

            if stype == 'building':
                b = Entity(model='cube', position=pos, scale=s_scale, color=col, collider='box')
                # Door entrance cutout visual
                door = Entity(parent=b, model='cube', position=(0, -0.3, -0.51), scale=(0.25, 0.5, 0.05), color=color.black)
                self.level_entities.extend([b, door])

            elif stype == 'guard_tower':
                tower = Entity(model='cube', position=pos, scale=s_scale, color=col, collider='box')
                top_platform = Entity(parent=tower, model='cube', position=(0, 0.5, 0), scale=(1.4, 0.1, 1.4), color=color.dark_gray)
                self.level_entities.extend([tower, top_platform])

            elif stype == 'radar_dish':
                base = Entity(model='cube', position=pos, scale=(s_scale.x*0.5, s_scale.y*0.6, s_scale.z*0.5), color=color.dark_gray, collider='box')
                dish = Entity(parent=base, model='sphere', position=(0, 0.8, 0), scale=(1.5, 0.3, 1.5), color=col)
                self.level_entities.extend([base, dish])

            elif stype == 'loot_crate':
                crate = Entity(model='cube', position=pos, scale=s_scale, color=col, collider='box')
                self.level_entities.append(crate)

    def generate_trees(self, count=25):
        random.seed(self.current_level_data.get('level', 1) * 100)
        for _ in range(count):
            tx = random.uniform(-65, 65)
            tz = random.uniform(-65, 65)
            # Avoid placing trees right next to spawn
            if sqrt(tx*tx + tz*tz) < 10:
                continue

            trunk = Entity(model='cube', position=(tx, 1.5, tz), scale=(0.5, 3, 0.5), color=color.brown, collider='box')
            leaves = Entity(parent=trunk, model='sphere', position=(0, 0.8, 0), scale=(4, 2, 4), color=color.rgb(40, 100, 40))
            self.level_entities.extend([trunk, leaves])

    def generate_objective(self):
        ext_pos = Vec3(*self.current_level_data.get('extraction_pos', [0, 1, 20]))
        obj_type = self.current_level_data.get('objective_type', 'HACK_TERMINAL')

        if obj_type in ['HACK_TERMINAL', 'RETRIEVE_INTEL', 'DESTROY_OBJECTIVE']:
            # Terminal / Laptop / Console Entity
            self.objective_entity = Entity(
                model='cube',
                position=ext_pos,
                scale=(1.2, 1.5, 1.2),
                color=color.cyan if obj_type == 'HACK_TERMINAL' else (color.yellow if obj_type == 'RETRIEVE_INTEL' else color.orange),
                collider='box'
            )
            # Objective Marker Overhead text
            label_text = "TERMINAL" if obj_type == 'HACK_TERMINAL' else ("INTEL" if obj_type == 'RETRIEVE_INTEL' else "TARGET OBJECTIVE")
            self.objective_marker = Text(parent=self.objective_entity, text=f'[{label_text}]\n(Press E)', y=1.5, scale=2, color=color.yellow, billboard=True)
            self.level_entities.append(self.objective_entity)

    def spawn_enemies(self, player):
        enemies_info = self.current_level_data.get('enemies', [])
        obj_type = self.current_level_data.get('objective_type', 'HACK_TERMINAL')

        for i, info in enumerate(enemies_info):
            pos = Vec3(*info.get('pos', [0, 1, 0]))
            wps = [Vec3(*wp) for wp in info.get('waypoints', [pos])]

            en = Enemy(position=pos, waypoints=wps)
            if player:
                en.set_player(player)

            # If ELIMINATE_TARGET objective, designate first enemy as Target Commander
            if obj_type == 'ELIMINATE_TARGET' and i == 0:
                en.color = color.gold
                en.scale = (1.2, 2.2, 1.2)
                en.status_indicator.text = 'TARGET COMMANDER'
                en.status_indicator.color = color.gold
                self.target_enemy = en

            self.enemies.append(en)

    def check_objective_interaction(self, player):
        obj_type = self.current_level_data.get('objective_type', 'HACK_TERMINAL')

        if obj_type == 'ELIMINATE_TARGET':
            if self.target_enemy and self.target_enemy.health <= 0:
                self.objective_completed = True
                return True, "TARGET ELIMINATED! Level Complete!"
            else:
                return False, f"Objective: Eliminate the Target Commander"

        if self.objective_entity and player:
            dist = distance(player.position, self.objective_entity.position)
            if dist < 3.0:
                if not self.objective_completed:
                    self.objective_completed = True
                    return True, "OBJECTIVE COMPLETED! Press E to Extract & Advance!"
                return True, "Press E to Extract & Advance!"

        return False, ""

    def notify_gunshot(self, origin_pos, noise_radius):
        for en in self.enemies:
            if en.health > 0:
                en.hear_gunshot(origin_pos, noise_radius)

    def get_alert_status(self):
        alert_count = sum(1 for e in self.enemies if e.health > 0 and e.state == "ALERT")
        caution_count = sum(1 for e in self.enemies if e.health > 0 and e.state == "Caution")

        if alert_count > 0:
            return "ALERT"
        elif caution_count > 0:
            return "Caution"
        return "Clear Patrol"
