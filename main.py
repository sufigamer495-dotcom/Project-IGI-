import os
from ursina import *

# Initialize Ursina App
app = Ursina(title="Project I.G.I. - 3D Tactical FPS", borderless=False)

from audio_generator import generate_all_audio
from weather_manager import WeatherManager
from level_manager import LevelManager
from player import Player
from hud import HUD

# Ensure sound assets are generated
generate_all_audio()

# Play looping ambient wind audio
try:
    wind_sound = Audio('assets/audio/wind.wav', loop=True, autoplay=True, volume=0.3)
except Exception as e:
    print("Audio warning:", e)

# Setup Game Systems
hud = HUD()
weather_manager = WeatherManager()
level_manager = LevelManager(weather_manager=weather_manager)
player = Player(hud=hud)

current_level_num = 1
level_manager.load_level(current_level_num, player=player)

game_over_screen = Entity(parent=camera.ui, enabled=False)
game_over_bg = Entity(parent=game_over_screen, model='quad', scale=(2, 2), color=color.rgba(0, 0, 0, 0.85))
game_over_text = Text(parent=game_over_screen, text='MISSION FAILED\nPress R to Restart Level', origin=(0, 0), scale=2, color=color.red)

victory_screen = Entity(parent=camera.ui, enabled=False)
victory_bg = Entity(parent=victory_screen, model='quad', scale=(2, 2), color=color.rgba(0, 0, 0, 0.85))
victory_text = Text(parent=victory_screen, text='ALL 20 MISSIONS COMPLETED!\nYOU ARE A TRUE I.G.I. AGENT!', origin=(0, 0), scale=2, color=color.gold)

is_game_over = False
is_game_won = False

def restart_current_level():
    global is_game_over
    is_game_over = False
    game_over_screen.enabled = False
    player.health = 100.0
    player.armor = 100.0
    player.stamina = 100.0
    level_manager.load_level(current_level_num, player=player)
    mouse.locked = True

def advance_to_next_level():
    global current_level_num, is_game_won
    current_level_num += 1
    if current_level_num > len(level_manager.levels_data):
        is_game_won = True
        victory_screen.enabled = True
        mouse.locked = False
    else:
        player.health = 100.0
        player.armor = 100.0
        player.stamina = 100.0
        level_manager.load_level(current_level_num, player=player)

def update():
    global is_game_over, is_game_won
    if is_game_won:
        return

    if player.health <= 0 and not is_game_over:
        is_game_over = True
        game_over_screen.enabled = True
        mouse.locked = False

    if is_game_over:
        if held_keys['r']:
            restart_current_level()
        return

    # Weather Particle Update
    weather_manager.update(player.position)

    # Level & Objective Check
    near_objective, prompt = level_manager.check_objective_interaction(player)
    hud.set_prompt(prompt)

    # Check gunshot noise from player shooting
    # Player handles shoot internally in update(), we hook gunshot listener
    if mouse.left:
        wpn = player.current_weapon
        if wpn and wpn.current_clip > 0 and (time.time() - wpn.last_shot_time < 0.05):
            level_manager.notify_gunshot(player.position, wpn.noise_radius)

    # Extraction 'E' Key
    if held_keys['e'] and near_objective:
        advance_to_next_level()

    # HUD updates
    lvl_data = level_manager.current_level_data
    hud.update_mission_info(
        level_name=f"{lvl_data['level']} - {lvl_data['name']}",
        objective=lvl_data['objective_text'],
        season=lvl_data.get('season', 'Winter'),
        alert_status=level_manager.get_alert_status()
    )

def input(key):
    if key == 'escape':
        mouse.locked = not mouse.locked

if __name__ == '__main__':
    app.run()
