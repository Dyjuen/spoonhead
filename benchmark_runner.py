import pygame
import psutil
import os
import time
import statistics
import random
import webbrowser
import json
import platform
from pathlib import Path
from main import Game
from sprites import Player, Platform, Enemy, BossGate
from settings import SCREEN_WIDTH, SCREEN_HEIGHT

class BenchmarkGame(Game):
    def __init__(self, duration=20):
        super().__init__()
        self.duration = duration
        self.start_time = None
        
        # Metrics Storage
        self.metrics = {
            'fps': [],
            'frametime': [],
            'cpu': [],
            'ram': [],
            'sprites': [],
            'timestamps': []
        }
        self.process = psutil.Process(os.getpid())
        
        # Level Setup
        self.all_sprites.empty()
        self.platforms.empty()
        self.enemies.empty()
        
        ground = Platform(-2000, 500, 10000, 50)
        self.all_sprites.add(ground)
        self.platforms.add(ground)

        wall_width = 50
        left_wall = Platform(0, 0, wall_width, SCREEN_HEIGHT)
        right_wall = Platform(SCREEN_WIDTH - wall_width, 0, wall_width, SCREEN_HEIGHT)
        self.all_sprites.add(left_wall, right_wall)
        self.platforms.add(left_wall, right_wall)
        
        self.boss_gate = BossGate(5000, 400)
        self.all_sprites.add(self.boss_gate)
        self.boss_gate_group.add(self.boss_gate)
        
        self.player = Player(400, 400, self, upgrades=self.upgrades, character_id='cyborg')
        self.player.health = 99999 
        self.all_sprites.add(self.player)
        
        self.player.unlocked_weapons.append('spread_shot')
        self.player.current_weapon_index = self.player.unlocked_weapons.index('spread_shot')
        
        self.game_state = 'platformer'
        self.start_time = time.time()
        print(f"--- Starting Advanced Benchmark with Graphs (Duration: {self.duration}s) ---")

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update_game_state(self):
        current_time = time.time()
        elapsed = current_time - self.start_time
        
        if self.clock.get_fps() > 0:
            self.metrics['fps'].append(round(self.clock.get_fps(), 1))
            self.metrics['frametime'].append(round(self.clock.get_time(), 1))
            self.metrics['cpu'].append(psutil.cpu_percent(interval=None))
            self.metrics['ram'].append(round(self.process.memory_info().rss / (1024 * 1024), 1))
            self.metrics['sprites'].append(len(self.all_sprites))
            self.metrics['timestamps'].append(round(elapsed, 1))

        if elapsed >= self.duration:
            self.running = False
            self.generate_report()
            return

        # Ramp up intensity
        target_enemies = 10 + int(elapsed * 3) # Up to ~70 enemies
        if len(self.enemies) < target_enemies:
            if random.random() < 0.3:
                ex = random.randint(100, SCREEN_WIDTH - 100)
                ey = random.randint(100, 400)
                enemy = Enemy(ex, ey, self.player, patrol_distance=200, speed=3)
                self.all_sprites.add(enemy)
                self.enemies.add(enemy)

        self.controller.get_actions = self.mock_stress_actions
        if self.player.health < 1000: self.player.health = 99999
        super().update_game_state()

    def mock_stress_actions(self):
        import math
        t = time.time()
        move_val = (math.sin(t * 3) + 1) / 2 
        directions = ['left', 'up_left', 'up', 'up_right', 'right', 'down_right', 'down', 'down_left']
        aim_dir = directions[int(t * 5) % 8]
        return {
            'move_x': move_val, 
            'jump': random.random() < 0.08,
            'dash': random.random() < 0.03,
            'shoot': True, 
            'shoot_direction': aim_dir,
            'switch_weapon': False,
            'activate_ultimate': random.random() < 0.01
        }

    def generate_report(self):
        if not self.metrics['fps']: return

        fps_data = self.metrics['fps']
        cpu_data = self.metrics['cpu']
        time_data = self.metrics['timestamps']
        
        avg_fps = statistics.mean(fps_data)
        max_fps = max(fps_data)
        min_fps = min(fps_data)
        
        # 1% Lows
        sorted_fps = sorted(fps_data)
        one_percent_idx = max(1, int(len(fps_data) * 0.01))
        low_1_percent = statistics.mean(sorted_fps[:one_percent_idx])
        
        # Stability Categories for Pie Chart
        smooth = len([x for x in fps_data if x >= 58])
        playable = len([x for x in fps_data if 30 <= x < 58])
        stutter = len([x for x in fps_data if x < 30])
        total_frames = len(fps_data)
        
        max_cpu = max(cpu_data)
        max_ram = max(self.metrics['ram'])

        verdict_color = "#4caf50" if low_1_percent > 50 else "#ff9800" if low_1_percent > 30 else "#f44336"
        verdict_text = "EXCELLENT" if low_1_percent > 50 else "PLAYABLE" if low_1_percent > 30 else "POOR"

        # Hardware Info
        sys_info = {
            "OS": f"{platform.system()} {platform.release()}",
            "Processor": platform.processor() or "Unknown Architecture",
            "Total RAM": f"{round(psutil.virtual_memory().total / (1024**3), 1)} GB",
            "Python": platform.python_version()
        }

        # Embed data as JSON for JS
        fps_json = json.dumps(fps_data)
        cpu_json = json.dumps(cpu_data)
        time_json = json.dumps(time_data)
        pie_data_json = json.dumps([smooth, playable, stutter])

        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Spoonhead Benchmark</title>
    <style>
        :root {{ --bg: #121212; --card: #1e1e1e; --text: #e0e0e0; --accent: {verdict_color}; }}
        body {{ font-family: 'Segoe UI', sans-serif; background: var(--bg); color: var(--text); padding: 40px; }}
        .container {{ max_width: 1100px; margin: 0 auto; }}
        
        header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 40px; border-bottom: 1px solid #333; padding-bottom: 20px; }}
        h1 {{ margin: 0; font-size: 2.2rem; }}
        .subtitle {{ color: #888; font-size: 0.9rem; }}
        .btn-print {{ background: #333; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; transition: 0.2s; }}
        .btn-print:hover {{ background: #555; }}

        .layout-grid {{ display: grid; grid-template-columns: 2fr 1fr; gap: 20px; }}
        
        /* Hardware Specs */
        .specs-box {{ background: var(--card); padding: 20px; border-radius: 12px; margin-bottom: 20px; display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; }}
        .spec-item .label {{ color: #777; font-size: 0.75rem; text-transform: uppercase; }}
        .spec-item .val {{ font-weight: 600; font-size: 0.95rem; margin-top: 4px; }}

        /* Main Cards */
        .metric-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 20px; }}
        .card {{ background: var(--card); padding: 20px; border-radius: 12px; text-align: center; border-top: 3px solid #333; position: relative; }}
        .card.main {{ border-top-color: var(--accent); grid-column: span 4; display: flex; justify-content: space-between; align-items: center; padding: 30px; }}
        
        .metric-val {{ font-size: 2rem; font-weight: bold; }}
        .metric-lbl {{ color: #aaa; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px; }}
        
        /* Charts */
        .chart-box {{ background: var(--card); padding: 20px; border-radius: 12px; margin-bottom: 20px; height: 350px; }}
        .chart-box.small {{ height: 300px; }}
    </style>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <div class="container">
        <header>
            <div>
                <h1>🥄 SPOONHEAD BENCHMARK</h1>
                <div class="subtitle">{time.strftime('%Y-%m-%d %H:%M:%S')} • Duration: {self.duration}s • Stress Test</div>
            </div>
            <button class="btn-print" onclick="window.print()">🖨️ Print Report</button>
        </header>

        <div class="specs-box">
            <div class="spec-item">
                <div class="label">Operating System</div>
                <div class="val">{sys_info['OS']}</div>
            </div>
            <div class="spec-item">
                <div class="label">Processor</div>
                <div class="val">{sys_info['Processor']}</div>
            </div>
            <div class="spec-item">
                <div class="label">System Memory</div>
                <div class="val">{sys_info['Total RAM']}</div>
            </div>
            <div class="spec-item">
                <div class="label">Engine</div>
                <div class="val">Pygame 2.x (Python {sys_info['Python']})</div>
            </div>
        </div>

        <div class="layout-grid">
            <!-- LEFT COLUMN -->
            <div>
                <div class="metric-grid">
                    <div class="card main">
                        <div style="text-align:left">
                            <div class="metric-val" style="color:var(--accent)">{verdict_text}</div>
                            <div class="metric-lbl">Overall Rating</div>
                        </div>
                        <div style="text-align:right">
                            <div class="metric-val">{low_1_percent:.1f} FPS</div>
                            <div class="metric-lbl">1% Low (Stability)</div>
                        </div>
                    </div>
                    
                    <div class="card">
                        <div class="metric-val">{avg_fps:.1f}</div>
                        <div class="metric-lbl">Avg FPS</div>
                    </div>
                    <div class="card">
                        <div class="metric-val">{max_cpu:.1f}%</div>
                        <div class="metric-lbl">Peak CPU</div>
                    </div>
                    <div class="card">
                        <div class="metric-val">{max_ram:.0f} MB</div>
                        <div class="metric-lbl">Peak RAM</div>
                    </div>
                    <div class="card">
                        <div class="metric-val">{max(self.metrics['sprites'])}</div>
                        <div class="metric-lbl">Max Sprites</div>
                    </div>
                </div>

                <div class="chart-box">
                    <canvas id="lineChart"></canvas>
                </div>
            </div>

            <!-- RIGHT COLUMN -->
            <div>
                <div class="chart-box small">
                    <h4 style="margin: 0 0 15px 0; text-align: center; color: #888;">Frame Consistency</h4>
                    <canvas id="pieChart"></canvas>
                </div>
                
                <div class="card" style="text-align: left; height: auto;">
                    <div class="metric-lbl" style="margin-bottom: 10px;">Benchmark Notes</div>
                    <p style="font-size: 0.85rem; color: #888; line-height: 1.5;">
                        This test simulates a worst-case "Horde Mode" scenario with up to 70 active enemies and continuous projectile rendering. 
                        <br><br>
                        <strong>Score Guide:</strong><br>
                        <span style="color:#4caf50">■</span> >50 FPS: Competitive Ready<br>
                        <span style="color:#ff9800">■</span> >30 FPS: Casual Playable<br>
                        <span style="color:#f44336">■</span> <30 FPS: Upgrade Required
                    </p>
                </div>
            </div>
        </div>

        <script>
            // Line Chart
            new Chart(document.getElementById('lineChart'), {{
                type: 'line',
                data: {{
                    labels: {time_json},
                    datasets: [
                        {{
                            label: 'FPS',
                            data: {fps_json},
                            borderColor: '#4caf50',
                            borderWidth: 2,
                            tension: 0.4,
                            pointRadius: 0,
                            yAxisID: 'y'
                        }},
                        {{
                            label: 'CPU %',
                            data: {cpu_json},
                            borderColor: '#f44336',
                            borderWidth: 1,
                            borderDash: [5, 5],
                            pointRadius: 0,
                            tension: 0.4,
                            yAxisID: 'y1'
                        }}
                    ]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: {{ mode: 'index', intersect: false }},
                    scales: {{
                        y: {{ min: 0, max: 144, grid: {{color: '#333'}} }},
                        y1: {{ position: 'right', min: 0, max: 100, grid: {{display: false}} }}
                    }},
                    plugins: {{ legend: {{ labels: {{ color: '#ccc' }} }} }}
                }}
            }});

            // Pie Chart
            new Chart(document.getElementById('pieChart'), {{
                type: 'doughnut',
                data: {{
                    labels: ['Smooth (60+)', 'Playable (30-59)', 'Laggy (<30)'],
                    datasets: [{{
                        data: {pie_data_json},
                        backgroundColor: ['#4caf50', '#ff9800', '#f44336'],
                        borderWidth: 0
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{ legend: {{ position: 'bottom', labels: {{ color: '#ccc', padding: 20 }} }} }}
                }}
            }});
        </script>
    </div>
</body>
</html>
"""
        # Save HTML
        report_path = Path("benchmark_report.html").absolute()
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(html)
        
        print("Report generated successfully.")
        
        # Robust Auto-Open
        try:
            webbrowser.open(report_path.as_uri())
        except:
            pass

if __name__ == "__main__":
    print("Initializing Advanced Stress Test...")
    os.environ['SDL_AUDIODRIVER'] = 'dummy'
    game = BenchmarkGame(duration=20)
    game.run()
