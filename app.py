from flask import Flask, request, send_file
from PIL import Image, ImageDraw
import numpy as np
import os
import random
import io
import math

app = Flask(__name__)

def draw_jigsaw_segment(draw, start, end, fixed_pos, cell_size, amplitude, is_tab, direction):
    """Draw a jigsaw segment with proper shape"""
    points = []
    segment_length = end - start

    for i in range(0, int(segment_length), 2):  # Step by 2px for performance
        pos = start + i
        normalized = i / segment_length

        if direction == 'horizontal':
            if is_tab:
                # Create curved tab
                if 0.3 <= normalized <= 0.7:
                    wave = amplitude * math.sin((normalized - 0.3) * math.pi / 0.4)
                else:
                    wave = 0
            else:
                # Create curved socket
                if 0.3 <= normalized <= 0.7:
                    wave = -amplitude * math.sin((normalized - 0.3) * math.pi / 0.4)
                else:
                    wave = 0
            points.append((pos, fixed_pos + wave))
        else:
            if is_tab:
                if 0.3 <= normalized <= 0.7:
                    wave = amplitude * math.sin((normalized - 0.3) * math.pi / 0.4)
                else:
                    wave = 0
            else:
                if 0.3 <= normalized <= 0.7:
                    wave = -amplitude * math.sin((normalized - 0.3) * math.pi / 0.4)
                else:
                    wave = 0
            points.append((fixed_pos + wave, pos))

    if points and len(points) > 1:
        draw.line(points, fill=(0, 0, 0), width=4)

def create_simple_jigsaw(input_image, rows=6, cols=6, tab_size=25):
    """
    Simple but effective jigsaw puzzle with proper piece shapes
    """
    width, height = input_image.size
    result = input_image.copy()
    draw = ImageDraw.Draw(result)

    cell_width = width / cols
    cell_height = height / rows

    # Draw horizontal cuts (between rows)
    for row in range(1, rows):
        y = row * cell_height
        for col in range(cols):
            x_start = col * cell_width
            x_end = x_start + cell_width

            # Alternate between tab and socket for variety
            has_tab = (row + col) % 2 == 0

            # Draw jigsaw cut for this segment
            draw_jigsaw_segment(draw, x_start, x_end, y, cell_width, tab_size, has_tab, 'horizontal')

    # Draw vertical cuts (between columns)
    for col in range(1, cols):
        x = col * cell_width
        for row in range(rows):
            y_start = row * cell_height
            y_end = y_start + cell_height

            # Alternate pattern for vertical cuts
            has_tab = (row + col) % 3 == 0
            draw_jigsaw_segment(draw, y_start, y_end, x, cell_height, tab_size, has_tab, 'vertical')

    return result

def create_jigsaw_mask(width, height, rows, cols, tab_size):
    """Create a mask for the jigsaw puzzle pieces"""
    mask = Image.new('L', (width, height), 255)
    draw = ImageDraw.Draw(mask)

    cell_width = width / cols
    cell_height = height / rows

    # Draw horizontal cuts
    for row in range(1, rows):
        y = row * cell_height
        points = []
        for x in range(0, width, 2):
            cell_x = (x % cell_width) / cell_width
            if 0.3 <= cell_x <= 0.7:
                wave = tab_size * math.sin((cell_x - 0.3) * math.pi / 0.4)
            else:
                wave = 0
            points.append((x, y + wave))

        if points:
            draw.line(points, fill=0, width=3)

    # Draw vertical cuts
    for col in range(1, cols):
        x = col * cell_width
        points = []
        for y in range(0, height, 2):
            cell_y = (y % cell_height) / cell_height
            if 0.3 <= cell_y <= 0.7:
                wave = tab_size * math.sin((cell_y - 0.3) * math.pi / 0.4)
            else:
                wave = 0
            points.append((x + wave, y))

        if points:
            draw.line(points, fill=0, width=3)

    return mask

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>REAL Jigsaw Puzzle Creator</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 600px;
                margin: 50px auto;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            .container {
                background: rgba(255, 255, 255, 0.1);
                padding: 30px;
                border-radius: 15px;
                backdrop-filter: blur(10px);
            }
            h1 {
                text-align: center;
                margin-bottom: 30px;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }
            .form-group {
                margin: 20px 0;
            }
            label {
                display: block;
                margin-bottom: 8px;
                font-weight: bold;
            }
            input[type="file"],
            input[type="range"] {
                width: 100%;
                padding: 10px;
                border: none;
                border-radius: 5px;
                background: rgba(255, 255, 255, 0.2);
                color: white;
            }
            button {
                background: #ff6b6b;
                color: white;
                padding: 15px 30px;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                font-size: 18px;
                display: block;
                margin: 30px auto;
                width: 200px;
                transition: background 0.3s;
            }
            button:hover {
                background: #ee5a52;
            }
            .value-display {
                background: rgba(255, 255, 255, 0.2);
                padding: 5px 15px;
                border-radius: 20px;
                display: inline-block;
                margin-left: 10px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🧩 REAL Jigsaw Puzzle Creator</h1>
            <form method="post" action="/create" enctype="multipart/form-data">
                <div class="form-group">
                    <label for="image">Select Image:</label>
                    <input type="file" name="image" id="image" accept="image/*" required>
                </div>

                <div class="form-group">
                    <label for="pieces">
                        Number of Pieces: <span class="value-display" id="piecesValue">36</span>
                    </label>
                    <input type="range" name="pieces" id="pieces" min="9" max="60" value="36"
                           oninput="document.getElementById('piecesValue').textContent = this.value">
                </div>

                <div class="form-group">
                    <label for="tab_size">
                        Tab Size: <span class="value-display" id="tabSizeValue">25</span>
                    </label>
                    <input type="range" name="tab_size" id="tab_size" min="15" max="40" value="25"
                           oninput="document.getElementById('tabSizeValue').textContent = this.value">
                </div>

                <button type="submit">Create Jigsaw Puzzle</button>
            </form>
        </div>

        <script>
            document.addEventListener('DOMContentLoaded', function() {
                document.getElementById('piecesValue').textContent = document.getElementById('pieces').value;
                document.getElementById('tabSizeValue').textContent = document.getElementById('tab_size').value;
            });
        </script>
    </body>
    </html>
    '''

@app.route('/create', methods=['POST'])
def create_puzzle():
    if 'image' not in request.files:
        return 'No file uploaded', 400

    file = request.files['image']
    if file.filename == '':
        return 'No file selected', 400

    try:
        img = Image.open(file.stream).convert('RGB')
        pieces = min(int(request.form.get('pieces', 36)), 60)
        tab_size = int(request.form.get('tab_size', 25))

        # Calculate rows and cols for square grid
        grid_size = int(math.sqrt(pieces))
        rows = cols = grid_size

        # Create the jigsaw puzzle
        puzzle_img = create_simple_jigsaw(img, rows, cols, tab_size)

        img_io = io.BytesIO()
        puzzle_img.save(img_io, 'JPEG', quality=95)
        img_io.seek(0)

        return send_file(
            img_io,
            mimetype='image/jpeg',
            as_attachment=True,
            download_name='jigsaw_puzzle.jpg'
        )

    except Exception as e:
        return f'Error: {str(e)}', 500

if __name__ == '__main__':
    print("Starting Jigsaw Puzzle Creator...")
    print("Visit http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
