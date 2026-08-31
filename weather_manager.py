import random
from ursina import *

class Seasons:
    WINTER = "Winter"
    SPRING = "Spring"
    SUMMER = "Summer"
    AUTUMN = "Autumn"

class WeatherManager:
    def __init__(self, sky=None, ground=None):
        self.sky = sky
        self.ground = ground
        self.current_season = Seasons.WINTER

        self.snow_particles = []
        self.leaf_particles = []
        self.particle_container = Entity()

        # Season configuration profiles
        self.profiles = {
            Seasons.WINTER: {
                'sky_color': color.rgb(180, 200, 220),
                'ground_color': color.rgb(230, 235, 240),
                'particles': 'snow'
            },
            Seasons.SPRING: {
                'sky_color': color.rgb(135, 206, 235),
                'ground_color': color.rgb(80, 160, 60),
                'particles': 'none'
            },
            Seasons.SUMMER: {
                'sky_color': color.rgb(70, 150, 240),
                'ground_color': color.rgb(60, 180, 50),
                'particles': 'none'
            },
            Seasons.AUTUMN: {
                'sky_color': color.rgb(210, 160, 120),
                'ground_color': color.rgb(140, 100, 50),
                'particles': 'leaves'
            }
        }

    def set_season(self, season_name):
        if season_name not in self.profiles:
            season_name = Seasons.WINTER
        self.current_season = season_name
        prof = self.profiles[season_name]

        if self.sky:
            self.sky.color = prof['sky_color']
        if self.ground:
            self.ground.color = prof['ground_color']

        self.clear_particles()

        if prof['particles'] == 'snow':
            self.init_snow_particles()
        elif prof['particles'] == 'leaves':
            self.init_leaf_particles()

    def clear_particles(self):
        for p in self.snow_particles + self.leaf_particles:
            destroy(p)
        self.snow_particles.clear()
        self.leaf_particles.clear()

    def init_snow_particles(self, num_particles=80):
        for _ in range(num_particles):
            p = Entity(
                parent=self.particle_container,
                model='quad',
                color=color.white,
                scale=0.1,
                position=(random.uniform(-40, 40), random.uniform(5, 25), random.uniform(-40, 40)),
                billboard=True
            )
            p.fall_speed = random.uniform(2.0, 5.0)
            p.drift_speed = random.uniform(-0.5, 0.5)
            self.snow_particles.append(p)

    def init_leaf_particles(self, num_particles=60):
        colors = [color.rgb(200, 80, 20), color.rgb(220, 150, 30), color.rgb(180, 50, 20)]
        for _ in range(num_particles):
            p = Entity(
                parent=self.particle_container,
                model='quad',
                color=random.choice(colors),
                scale=random.uniform(0.12, 0.2),
                position=(random.uniform(-40, 40), random.uniform(5, 25), random.uniform(-40, 40)),
                rotation=(random.uniform(0, 360), random.uniform(0, 360), 0)
            )
            p.fall_speed = random.uniform(1.5, 3.5)
            p.sway_freq = random.uniform(1.0, 3.0)
            p.sway_amp = random.uniform(0.5, 1.5)
            p.initial_x = p.x
            self.leaf_particles.append(p)

    def update(self, player_pos=None):
        center_x = player_pos.x if player_pos else 0
        center_z = player_pos.z if player_pos else 0

        dt = time.dt
        # Update snow particles
        for p in self.snow_particles:
            p.y -= p.fall_speed * dt
            p.x += p.drift_speed * dt
            if p.y < 0:
                p.y = random.uniform(15, 25)
                p.x = center_x + random.uniform(-40, 40)
                p.z = center_z + random.uniform(-40, 40)

        # Update leaf particles
        for p in self.leaf_particles:
            p.y -= p.fall_speed * dt
            p.x += math.sin(time.time() * p.sway_freq) * p.sway_amp * dt
            p.rotation_z += 50 * dt
            if p.y < 0:
                p.y = random.uniform(15, 25)
                p.x = center_x + random.uniform(-40, 40)
                p.z = center_z + random.uniform(-40, 40)
