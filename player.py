from ursina import *
from weapons import create_default_weapons

class Player(Entity):
    def __init__(self, position=(0, 2, 0), hud=None, **kwargs):
        super().__init__(**kwargs)
        self.position = position
        self.hud = hud

        # Stats
        self.health = 100.0
        self.max_health = 100.0
        self.armor = 100.0
        self.max_armor = 100.0
        self.stamina = 100.0
        self.max_stamina = 100.0

        # Movement specs
        self.walk_speed = 7.0
        self.sprint_speed = 12.0
        self.speed = self.walk_speed
        self.stamina_drain = 20.0  # per second when sprinting
        self.stamina_recovery = 15.0  # per second when walking/idle

        # Camera & Mouse Look setup
        camera.parent = self
        camera.position = (0, 1.6, 0)
        camera.rotation = (0, 0, 0)
        camera.fov = 90
        mouse.locked = True

        # Weapons
        self.weapons = create_default_weapons()
        self.current_weapon_slot = 1
        self.current_weapon = self.weapons[1]
        self.is_scoped = False

        # Visual Weapon model in hand
        self.weapon_model = Entity(parent=camera, model='cube', scale=(0.1, 0.1, 0.4), position=(0.3, -0.2, 0.5), color=color.dark_gray)

        # Audio instances cache
        self.audio_cache = {}

    def play_sound(self, sound_path):
        if sound_path not in self.audio_cache:
            self.audio_cache[sound_path] = Audio(sound_path, autoplay=False, loop=False)
        snd = self.audio_cache[sound_path]
        if snd:
            snd.play()

    def update(self):
        self.handle_movement()
        self.handle_weapon_input()
        self.update_stats()
        self.update_hud()

    def handle_movement(self):
        # Mouse look
        self.rotation_y += mouse.velocity[0] * 40
        camera.rotation_x -= mouse.velocity[1] * 40
        camera.rotation_x = clamp(camera.rotation_x, -85, 85)

        # Sprint logic
        is_moving = held_keys['w'] or held_keys['s'] or held_keys['a'] or held_keys['d']
        if held_keys['left shift'] and is_moving and self.stamina > 5:
            self.speed = self.sprint_speed
            self.stamina = max(0.0, self.stamina - self.stamina_drain * time.dt)
        else:
            self.speed = self.walk_speed
            self.stamina = min(self.max_stamina, self.stamina + self.stamina_recovery * time.dt)

        # WASD direction
        move_dir = Vec3(
            held_keys['d'] - held_keys['a'],
            0,
            held_keys['w'] - held_keys['s']
        ).normalized()

        # Raycast for ground collision / terrain clamping
        move_vec = (self.forward * move_dir.z + self.right * move_dir.x) * self.speed * time.dt
        self.position += move_vec

        # Keep player at y = 1.0 above ground
        ground_ray = raycast(self.position + Vec3(0, 5, 0), Vec3(0, -1, 0), ignore=(self,), distance=10)
        if ground_ray.hit:
            self.y = ground_ray.point.y + 1.0
        else:
            self.y = 1.0

    def handle_weapon_input(self):
        # Switch weapon 1, 2, 3
        if held_keys['1'] and self.current_weapon_slot != 1:
            self.switch_weapon(1)
        elif held_keys['2'] and self.current_weapon_slot != 2:
            self.switch_weapon(2)
        elif held_keys['3'] and self.current_weapon_slot != 3:
            self.switch_weapon(3)

        # Sniper Scope Aim (Right Mouse Button)
        if self.current_weapon_slot == 3 and mouse.right:
            if not self.is_scoped:
                self.is_scoped = True
                camera.fov = 30
                if self.hud:
                    self.hud.set_scoped(True)
        else:
            if self.is_scoped:
                self.is_scoped = False
                camera.fov = 90
                if self.hud:
                    self.hud.set_scoped(False)

        # Reloading (R)
        if held_keys['r']:
            if self.current_weapon.start_reload():
                self.play_sound('assets/audio/reload.wav')

        # Weapon update reload timer
        self.current_weapon.update_reload()

        # Shooting (Left Mouse Button)
        if mouse.left:
            self.shoot_weapon()

    def switch_weapon(self, slot):
        if slot in self.weapons:
            self.current_weapon_slot = slot
            self.current_weapon = self.weapons[slot]
            if self.is_scoped:
                self.is_scoped = False
                camera.fov = 90
                if self.hud:
                    self.hud.set_scoped(False)

            # Adjust weapon model appearance based on weapon type
            if slot == 1:
                self.weapon_model.scale = (0.08, 0.08, 0.3)
                self.weapon_model.color = color.dark_gray
            elif slot == 2:
                self.weapon_model.scale = (0.1, 0.12, 0.5)
                self.weapon_model.color = color.gray
            elif slot == 3:
                self.weapon_model.scale = (0.09, 0.1, 0.7)
                self.weapon_model.color = color.black

    def shoot_weapon(self):
        if self.current_weapon.shoot():
            self.play_sound(self.current_weapon.sound_file)

            # Weapon recoil effect
            camera.rotation_x -= 1.0

            # Raycast shooting hit check
            hit_info = raycast(camera.world_position, camera.forward, distance=100, ignore=(self,))

            # Broadcast gunshot event for enemy AI detection
            shoot_event_data = {
                'origin': self.position,
                'noise_radius': self.current_weapon.noise_radius,
                'weapon': self.current_weapon,
                'hit_info': hit_info
            }

            if hit_info.hit:
                # Bullet impact effect / damage
                if hasattr(hit_info.entity, 'take_damage'):
                    hit_info.entity.take_damage(self.current_weapon.damage)
                    self.play_sound('assets/audio/hit.wav')

            return shoot_event_data
        return None

    def take_damage(self, damage):
        # Armor absorbs 60% of damage
        if self.armor > 0:
            armor_damage = damage * 0.6
            hp_damage = damage * 0.4
            if self.armor >= armor_damage:
                self.armor -= armor_damage
            else:
                hp_damage += (armor_damage - self.armor)
                self.armor = 0
            self.health -= hp_damage
        else:
            self.health -= damage

        self.health = max(0.0, self.health)

    def update_stats(self):
        pass

    def update_hud(self):
        if self.hud:
            self.hud.update_stats(self.health, self.max_health, self.armor, self.max_armor, self.stamina, self.max_stamina)
            self.hud.update_weapon_info(self.current_weapon.name, self.current_weapon.current_clip, self.current_weapon.reserve_ammo, self.current_weapon.is_reloading)
