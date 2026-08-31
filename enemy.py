import math
import time
from ursina import *

class AlertState:
    PATROL = "Clear Patrol"
    CAUTION = "Caution"
    ALERT = "ALERT"

class Enemy(Entity):
    def __init__(self, waypoints=None, health=100, field_of_view=90, view_distance=25, **kwargs):
        super().__init__(
            model='cube',
            color=color.rgb(200, 30, 30),
            scale=(1, 2, 1),
            collider='box',
            **kwargs
        )
        self.health = health
        self.max_health = health
        self.waypoints = waypoints or [self.position]
        self.current_waypoint_idx = 0
        self.field_of_view = field_of_view
        self.view_distance = view_distance

        # AI State Machine
        self.state = AlertState.PATROL
        self.caution_timer = 0.0
        self.caution_duration = 3.0  # Seconds in caution before returning to patrol if target lost

        # Movement & Combat
        self.patrol_speed = 3.0
        self.alert_speed = 6.0
        self.attack_range = 18.0
        self.fire_rate = 0.8  # Time between enemy shots
        self.last_shot_time = 0
        self.damage = 10

        self.target_player = None
        self.last_known_player_pos = None

        # Visual indicator overhead
        self.status_indicator = Text(parent=self, text='PATROL', y=1.2, scale=2, color=color.green, billboard=True)

    def set_player(self, player):
        self.target_player = player

    def update(self):
        if self.health <= 0:
            return

        if not self.target_player:
            return

        # Check line-of-sight vision to player
        can_see = self.check_line_of_sight()

        # Update Alert State Machine
        self.update_state_machine(can_see)

        # Execute actions according to state
        if self.state == AlertState.PATROL:
            self.patrol_behavior()
            self.status_indicator.text = 'PATROL'
            self.status_indicator.color = color.green
        elif self.state == AlertState.CAUTION:
            self.caution_behavior()
            self.status_indicator.text = 'CAUTION'
            self.status_indicator.color = color.yellow
        elif self.state == AlertState.ALERT:
            self.alert_behavior()
            self.status_indicator.text = 'ALERT!'
            self.status_indicator.color = color.red

    def check_line_of_sight(self):
        if not self.target_player:
            return False

        dist = distance(self.position, self.target_player.position)
        if dist > self.view_distance:
            return False

        # Direction vector to player
        to_player = (self.target_player.position - self.position).normalized()

        # Check angle relative to enemy facing forward
        angle = Vec3.angle(self.forward, to_player)
        if angle > (self.field_of_view / 2.0):
            return False

        # Raycast check for obstacles blocking view
        hit_info = raycast(self.world_position + Vec3(0, 1, 0), to_player, distance=dist, ignore=(self,))
        if hit_info.hit and hit_info.entity == self.target_player:
            return True

        return False

    def update_state_machine(self, can_see_player):
        if can_see_player:
            self.state = AlertState.ALERT
            self.last_known_player_pos = Vec3(self.target_player.position)
            self.caution_timer = 0.0
        else:
            if self.state == AlertState.ALERT:
                # Transition to Caution when losing line of sight
                self.state = AlertState.CAUTION
                self.caution_timer = time.time()
            elif self.state == AlertState.CAUTION:
                if time.time() - self.caution_timer > self.caution_duration:
                    self.state = AlertState.PATROL

    def hear_gunshot(self, origin_pos, noise_radius):
        dist = distance(self.position, origin_pos)
        if dist <= noise_radius:
            if self.state == AlertState.PATROL:
                self.state = AlertState.CAUTION
                self.last_known_player_pos = Vec3(origin_pos)
                self.caution_timer = time.time()

    def patrol_behavior(self):
        if not self.waypoints:
            return

        target_wp = self.waypoints[self.current_waypoint_idx]
        target_pos = Vec3(target_wp.x, self.y, target_wp.z) if isinstance(target_wp, (Vec3, Entity)) else Vec3(target_wp[0], self.y, target_wp[2] if len(target_wp) > 2 else target_wp[1])

        dir_vec = (target_pos - self.position)
        dist = dir_vec.length()

        if dist < 0.8:
            self.current_waypoint_idx = (self.current_waypoint_idx + 1) % len(self.waypoints)
        else:
            dir_norm = dir_vec.normalized()
            self.look_at_2d(target_pos)
            self.position += dir_norm * self.patrol_speed * time.dt

    def caution_behavior(self):
        if self.last_known_player_pos:
            target_pos = Vec3(self.last_known_player_pos.x, self.y, self.last_known_player_pos.z)
            dir_vec = (target_pos - self.position)
            if dir_vec.length() > 1.0:
                self.look_at_2d(target_pos)
                self.position += dir_vec.normalized() * self.patrol_speed * time.dt

    def alert_behavior(self):
        if not self.target_player:
            return

        player_pos = Vec3(self.target_player.x, self.y, self.target_player.z)
        dir_vec = (player_pos - self.position)
        dist = dir_vec.length()

        self.look_at_2d(player_pos)

        if dist > 5.0:
            # Move towards player
            self.position += dir_vec.normalized() * self.alert_speed * time.dt

        # Fire back at player
        if dist <= self.attack_range:
            curr_time = time.time()
            if curr_time - self.last_shot_time >= self.fire_rate:
                self.last_shot_time = curr_time
                if hasattr(self.target_player, 'take_damage'):
                    self.target_player.take_damage(self.damage)

    def look_at_2d(self, target_pos):
        # Rotate y-axis towards target pos
        diff = target_pos - self.position
        angle = math.atan2(diff.x, diff.z)
        self.rotation_y = math.degrees(angle)

    def take_damage(self, damage):
        self.health -= damage
        self.state = AlertState.ALERT
        if self.target_player:
            self.last_known_player_pos = Vec3(self.target_player.position)

        if self.health <= 0:
            self.die()

    def die(self):
        self.visible = False
        self.collider = None
        self.status_indicator.enabled = False
