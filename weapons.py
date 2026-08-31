import os
import time

class Weapon:
    def __init__(self, name, slot, damage, fire_rate, clip_size, max_reserve, noise_radius, sound_file):
        self.name = name
        self.slot = slot
        self.damage = damage
        self.fire_rate = fire_rate  # Time delay between shots in seconds
        self.clip_size = clip_size
        self.current_clip = clip_size
        self.reserve_ammo = max_reserve
        self.max_reserve = max_reserve
        self.noise_radius = noise_radius
        self.sound_file = sound_file
        self.last_shot_time = 0
        self.is_reloading = False
        self.reload_start_time = 0
        self.reload_duration = 1.5  # Seconds

    def can_shoot(self):
        current_time = time.time()
        if self.is_reloading:
            if current_time - self.reload_start_time >= self.reload_duration:
                self.finish_reload()
            else:
                return False
        return self.current_clip > 0 and (current_time - self.last_shot_time >= self.fire_rate)

    def shoot(self):
        if not self.can_shoot():
            return False
        self.current_clip -= 1
        self.last_shot_time = time.time()
        return True

    def start_reload(self):
        if self.is_reloading or self.current_clip == self.clip_size or self.reserve_ammo == 0:
            return False
        self.is_reloading = True
        self.reload_start_time = time.time()
        return True

    def finish_reload(self):
        needed = self.clip_size - self.current_clip
        to_add = min(needed, self.reserve_ammo)
        self.current_clip += to_add
        self.reserve_ammo -= to_add
        self.is_reloading = False

    def update_reload(self):
        if self.is_reloading and (time.time() - self.reload_start_time >= self.reload_duration):
            self.finish_reload()
            return True
        return False

def create_default_weapons():
    return {
        1: Weapon("Suppressed Pistol", 1, damage=35, fire_rate=0.25, clip_size=12, max_reserve=48, noise_radius=10, sound_file="assets/audio/shot_pistol.wav"),
        2: Weapon("Assault Rifle", 2, damage=25, fire_rate=0.1, clip_size=30, max_reserve=120, noise_radius=45, sound_file="assets/audio/shot_rifle.wav"),
        3: Weapon("Sniper Rifle", 3, damage=100, fire_rate=1.0, clip_size=5, max_reserve=20, noise_radius=70, sound_file="assets/audio/shot_sniper.wav")
    }
