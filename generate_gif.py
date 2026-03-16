import os
import time
from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT = 900, 600
BG_COLOR = "#0D1117"
TERMINAL_BG = "#0d1117"
TERMINAL_TEXT = "#c9d1d9"
ACCENT_GREEN = "#238636"
ACCENT_BLUE = "#58a6ff"
ACCENT_MAGENTA = "#bc8cff"
ACCENT_YELLOW = "#e3b341"
ACCENT_RED = "#f85149"

os.makedirs("images", exist_ok=True)

try:
    font = ImageFont.truetype("/System/Library/Fonts/Monaco.ttf", 16)
    font_bold = ImageFont.truetype("/System/Library/Fonts/Monaco.ttf", 16)
    font_large = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 28)
except:
    font = ImageFont.load_default()
    font_bold = ImageFont.load_default()
    font_large = ImageFont.load_default()

def draw_mac_window(draw, w, h):
    draw.rounded_rectangle([(0, 0), (w, h)], 12, fill=TERMINAL_BG, outline="#30363d", width=2)
    # Mac buttons
    draw.ellipse([15, 15, 27, 27], fill="#ff5f56")
    draw.ellipse([35, 15, 47, 27], fill="#ffbd2e")
    draw.ellipse([55, 15, 67, 27], fill="#27c93f")
    draw.line([(0, 45), (w, 45)], fill="#30363d", width=2)

def create_frame(lines, show_cursor=False, cursor_pos=(0, 0), is_ui=False, ui_data=None):
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)
    
    if not is_ui:
        # Terminal Mode
        window_w, window_h = WIDTH - 80, HEIGHT - 100
        offset_x, offset_y = 40, 50
        
        # Draw shadow
        draw.rounded_rectangle([(offset_x+10, offset_y+10), (offset_x+window_w+10, offset_y+window_h+10)], 12, fill="#000000")
        
        # Draw Window
        draw.rounded_rectangle([(offset_x, offset_y), (offset_x+window_w, offset_y+window_h)], 12, fill=TERMINAL_BG, outline="#30363d", width=2)
        
        # Draw Mac Buttons
        draw.ellipse([offset_x+15, offset_y+15, offset_x+27, offset_y+27], fill="#ff5f56")
        draw.ellipse([offset_x+35, offset_y+15, offset_x+47, offset_y+27], fill="#ffbd2e")
        draw.ellipse([offset_x+55, offset_y+15, offset_x+67, offset_y+27], fill="#27c93f")
        draw.line([(offset_x, offset_y+45), (offset_x+window_w, offset_y+45)], fill="#30363d", width=1)
        
        text_y = offset_y + 60
        for line in lines:
            text = line.get("text", "")
            color = line.get("color", TERMINAL_TEXT)
            draw.text((offset_x + 20, text_y), text, fill=color, font=font)
            text_y += 24
            
        if show_cursor:
            cx, cy = cursor_pos
            draw.rectangle([offset_x + 20 + cx, offset_y + 60 + cy, offset_x + 30 + cx, offset_y + 78 + cy], fill="#ffffff")
    else:
        # UI Mode (Status Dashboard)
        draw.rectangle([0, 0, WIDTH, HEIGHT], fill="#f3f4f6")
        
        # Header
        draw.rectangle([0, 0, WIDTH, 80], fill="#1e293b")
        draw.text((40, 25), "DefectRouter-AI Dashboard", fill="#ffffff", font=font_large)
        
        if ui_data:
            cards = [
                ("Diagnostic Agent", "Active", ACCENT_MAGENTA, 40, 120),
                ("Calibration Agent", "Idle", ACCENT_GREEN, 460, 120),
                ("Maintenance Agent", "Routing Work Orders", ACCENT_RED, 40, 260),
                ("Material Agent", "Idle", ACCENT_YELLOW, 460, 260)
            ]
            
            for title, status, color, x, y in cards:
                draw.rounded_rectangle([x, y, x+400, y+100], 10, fill="#ffffff", outline="#e2e8f0", width=2)
                draw.rectangle([x, y, x+10, y+100], fill=color) # Left border color
                draw.text((x+30, y+20), title, fill="#1e293b", font=font_bold)
                draw.text((x+30, y+60), f"Status: {status}", fill="#64748b", font=font)
            
            # Bottom table
            draw.rounded_rectangle([40, 400, 860, 560], 10, fill="#ffffff", outline="#e2e8f0", width=2)
            draw.rectangle([40, 400, 860, 450], fill="#f8fafc")
            draw.line([40, 450, 860, 450], fill="#e2e8f0", width=2)
            draw.text((60, 415), "INCIDENT ID", fill="#64748b", font=font)
            draw.text((250, 415), "DEFECT TYPE", fill="#64748b", font=font)
            draw.text((450, 415), "SEVERITY", fill="#64748b", font=font)
            draw.text((650, 415), "RESOLUTION", fill="#64748b", font=font)
            
            draw.text((60, 470), "INC-88A92", fill="#0f172a", font=font)
            draw.text((250, 470), "Maintenance", fill="#0f172a", font=font)
            
            # Severity Badge
            draw.rounded_rectangle([445, 465, 510, 490], 12, fill="#fee2e2")
            draw.text((455, 470), "High", fill="#991b1b", font=font)
            
            draw.text((650, 470), "Work Order #992 Esc...", fill="#0f172a", font=font)
            
    return img

def main():
    frames = []
    
    # 1. Typing command
    cmd = "python main.py"
    for i in range(len(cmd) + 1):
        lines = [{"text": f"aniket@macbook:~/workspace$ {cmd[:i]}", "color": "#27c93f"}]
        # Estimate cursor x roughly
        pos_x = len(f"aniket@macbook:~/workspace$ {cmd[:i]}") * 9.6
        frames.append(create_frame(lines, show_cursor=True, cursor_pos=(int(pos_x), 0)))
        if i == len(cmd):
            # blinking cursor
            for _ in range(3):
                frames.append(create_frame(lines, show_cursor=False, cursor_pos=(int(pos_x), 0)))
                frames.append(create_frame(lines, show_cursor=True, cursor_pos=(int(pos_x), 0)))
    
    # Execution lines
    exec_logs = [
        {"text": "aniket@macbook:~/workspace$ python main.py", "color": "#27c93f"},
        {"text": "", "color": TERMINAL_TEXT},
        {"text": "╭────────────────────────────────────────────────────────────────╮", "color": ACCENT_BLUE},
        {"text": "│ DefectRouter-AI                                                │", "color": ACCENT_BLUE},
        {"text": "│ Multi-Agent Manufacturing Quality Control & Triaging System    │", "color": ACCENT_BLUE},
        {"text": "│ Powered by LangGraph and Advanced Communication Protocol       │", "color": "#8b949e"},
        {"text": "╰────────────────────────────────────────────────────────────────╯", "color": ACCENT_BLUE},
        {"text": "", "color": TERMINAL_TEXT},
        {"text": "🚨 New Incident Detected: INC-88A92", "color": "#ffffff"},
        {"text": "Incoming Sensor Payload: {\"machine_id\": \"CNC-Milli-04\", \"vib\": 6.2, \"temp\": 75}", "color": "#8b949e"},
        {"text": "", "color": TERMINAL_TEXT},
        {"text": "[SYSTEM] Initialization Sequence Started...", "color": ACCENT_BLUE},
        {"text": "10:14:02 Diagnostic Agent ➜ Analyzing sensor data for incident INC-88A92...", "color": ACCENT_MAGENTA},
        {"text": "10:14:03 Diagnostic Agent ➜ Evaluated heuristics. Reason: High vibration...", "color": ACCENT_MAGENTA},
        {"text": "10:14:04 Diagnostic Agent ➜ Diagnosis complete. Type: Maintenance (High)", "color": ACCENT_MAGENTA},
        {"text": "10:14:05 Maintenance Agent ➜ High wear detected. Generating work order...", "color": ACCENT_RED},
        {"text": "10:14:06 Maintenance Agent ➜ Work order #992 generated. Escalated...", "color": ACCENT_RED},
        {"text": "", "color": TERMINAL_TEXT},
        {"text": "✅ Incident Processing Complete.", "color": ACCENT_GREEN},
        {"text": "", "color": TERMINAL_TEXT},
        {"text": "Incident Summary Report", "color": ACCENT_MAGENTA},
        {"text": "┏━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓", "color": TERMINAL_TEXT},
        {"text": "┃ Property           ┃ Value                                    ┃", "color": TERMINAL_TEXT},
        {"text": "┡━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩", "color": TERMINAL_TEXT},
        {"text": "│ Incident ID        │ INC-88A92                                │", "color": TERMINAL_TEXT},
        {"text": "│ Defect Type        │ Maintenance                              │", "color": TERMINAL_TEXT},
        {"text": "│ Severity           │ High                                     │", "color": TERMINAL_TEXT},
        {"text": "│ Resolution Plan    │ Dispatching technician to inspect...     │", "color": TERMINAL_TEXT},
        {"text": "└────────────────────┴──────────────────────────────────────────┘", "color": TERMINAL_TEXT},
        {"text": "aniket@macbook:~/workspace$ ", "color": "#27c93f"}
    ]
    
    current_lines = [exec_logs[0]]
    for i in range(1, len(exec_logs)):
        if "Agent" in exec_logs[i]["text"] or "[SYSTEM]" in exec_logs[i]["text"]:
            for _ in range(3): # Hold frame
                frames.append(create_frame(current_lines))
        current_lines.append(exec_logs[i])
        frames.append(create_frame(current_lines))
        
    for _ in range(10): # Hold final terminal state
        frames.append(create_frame(current_lines))
        
    # Transition to UI
    for i in range(5):
        alpha = int(255 * (i/5))
        # We will just append the UI frames to simulate a hard cut/fade
        pass
        
    # UI Frames
    for _ in range(15):
        frames.append(create_frame([], is_ui=True, ui_data=True))

    # STRICT LINKEDIN COMPATIBILITY (Global Palette & No Dither)
    print("Generating global palette and quantizing frames...")
    sample = Image.new("RGB", (WIDTH, HEIGHT * 3))
    sample.paste(frames[0], (0, 0))
    sample.paste(frames[len(frames)//2], (0, HEIGHT))
    sample.paste(frames[-1], (0, HEIGHT * 2))
    
    palette = sample.quantize(colors=256, method=2)
    final_frames = [f.quantize(palette=palette, dither=Image.Dither.NONE) for f in frames]
    
    output_path = "images/title-animation.gif"
    final_frames[0].save(
        output_path, 
        save_all=True, 
        append_images=final_frames[1:], 
        optimize=True, 
        duration=100, 
        loop=0
    )
    print(f"Generated {output_path}")

if __name__ == "__main__":
    main()
