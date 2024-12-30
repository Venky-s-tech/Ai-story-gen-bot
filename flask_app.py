# app.py
from flask import Flask, render_template, request, jsonify, send_file
import os
import time
from werkzeug.utils import secure_filename
import base64
from io import BytesIO
from gtts import gTTS
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['AUDIO_FOLDER'] = 'audio'

# Ensure required folders exist
for folder in [app.config['UPLOAD_FOLDER'], app.config['AUDIO_FOLDER']]:
    if not os.path.exists(folder):
        os.makedirs(folder)

# Extended categories with more genres
categories = {
    'Hot Now': [
        {'title': 'Star-Crossed', 'image': '/static/placeholder.jpg', 'rating': '4.8'},
        {'title': 'The Dance', 'image': '/static/p1.jpg', 'rating': '4.6'},
        {'title': 'Night Tales', 'image': '/static/p2.jpg', 'rating': '4.7'}
    ],
    'Romance': [
        {'title': 'The Dance', 'image': '/static/p1.jpg', 'rating': '4.5'},
        {'title': 'Making it All', 'image': '/static/p3.jpg', 'rating': '4.3'},
        {'title': 'Last Love', 'image': '/static/p4.jpg', 'rating': '4.4'}
    ],
    'Horror': [
        {'title': 'The Haunting', 'image': '/static/p5.jpg', 'rating': '4.7'},
        {'title': 'Dark Manor', 'image': '/static/p6.jpg', 'rating': '4.6'},
        {'title': 'Whispers', 'image': '/static/p7.jpg', 'rating': '4.5'}
    ],
    'Science Fiction': [
        {'title': 'Space Odyssey', 'image': '/static/p8.jpg', 'rating': '4.9'},
        {'title': 'Time Warp', 'image': '/static/p9.jpg', 'rating': '4.7'},
        {'title': 'Android Dreams', 'image': '/static/p10.jpg', 'rating': '4.6'}
    ],
    'Comedy': [
        {'title': 'Laugh Track', 'image': '/static/p11.jpg', 'rating': '4.4'},
        {'title': 'Office Hours', 'image': '/static/p12.jpg', 'rating': '4.3'},
        {'title': 'Family Fun', 'image': '/static/p13.jpg', 'rating': '4.5'}
    ],
    'Historical': [
        {'title': 'Ancient Tales', 'image': '/static/p14.jpg', 'rating': '4.8'},
        {'title': 'War Stories', 'image': '/static/p15.jpg', 'rating': '4.7'},
        {'title': 'Royal Court', 'image': '/static/p16.jpg', 'rating': '4.6'}
    ]
}

theme_prompts = {
    "Horror": "Write a horror story using:",
    "Action": "Write a story with lots of action using: ",
    "Romance": "Write a romantic story using: ",
    "Comedy": "Write a funny story using: ",
    "Historical": "Write a story based on a historical event with the help of the input: ",
    "Science Fiction": "Write a science fiction story using: "
}

def generate_story_from_text(prompt):
    """Generate story based on text input"""
    # Simulate story generation with different themes
    theme = "default"
    for theme_key in theme_prompts:
        if theme_key.lower() in prompt.lower():
            theme = theme_key.lower()
            break
            
    time.sleep(2)  # Simulate API delay
    
    stories = {
        "horror": "In the dead of night, shadows crept along the walls. The old house creaked and moaned, as if warning of impending doom...",
        "action": "The chase was on! Tires screeched as the vehicles weaved through traffic. Time was running out, and the stakes couldn't be higher...",
        "romance": "Their eyes met across the crowded café. In that moment, the world seemed to pause, and everything else faded into the background...",
        "comedy": "Everything that could go wrong, did go wrong. And somehow, it was hilarious. The birthday cake wasn't supposed to end up on the ceiling...",
        "historical": "The year was 1789, and the streets of Paris were alive with revolution. Change was in the air, and history was about to be made...",
        "science fiction": "The alien spacecraft hovered silently above the city. Its presence changed everything we thought we knew about our place in the universe...",
        "default": "The story began on an ordinary day, but what happened next was anything but ordinary..."
    }
    
    return stories.get(theme, stories["default"]) + "\n\nBased on prompt: " + prompt

def generate_image_caption(image_file):
    """Generate caption for uploaded image"""
    # In a real application, you would use an image recognition API here
    captions = [
        "A stunning sunset over mountains",
        "A busy city street at night",
        "A peaceful garden in bloom",
        "A mysterious forest path",
        "A cozy café interior",
        "An ancient castle on a hill"
    ]
    import random
    time.sleep(2)  # Simulate API delay
    return random.choice(captions)

def generate_audio_from_story(text):
    """Generate audio file from story text"""
    try:
        # Generate a unique filename for each audio
        filename = f"story_{uuid.uuid4().hex[:8]}.mp3"
        filepath = os.path.join(app.config['AUDIO_FOLDER'], filename)
        
        # Generate audio using gTTS
        tts = gTTS(text=text, lang='en', slow=False)
        tts.save(filepath)
        
        return filename
    except Exception as e:
        print(f"Error generating audio: {str(e)}")
        return None

@app.route('/')
def index():
    return render_template('index.html', 
                         categories=categories,
                         theme_prompts=theme_prompts)

@app.route('/generate-story', methods=['POST'])
def generate_story():
    try:
        data = request.json
        input_type = data.get('inputType')
        selected_theme = data.get('selectedTheme')
        
        if input_type == 'text':
            input_text = data.get('inputText')
            prompt = f"{theme_prompts[selected_theme]} {input_text}"
            story = generate_story_from_text(prompt)
        else:
            image_data = data.get('uploadedImage')
            if not image_data:
                return jsonify({'error': 'Please upload an image first'}), 400
                
            # Process base64 image
            image_data = image_data.split(',')[1]
            image_binary = base64.b64decode(image_data)
            
            # Save temporary file
            temp_path = os.path.join(app.config['UPLOAD_FOLDER'], 'temp_image.jpg')
            with open(temp_path, 'wb') as f:
                f.write(image_binary)
            
            caption = generate_image_caption(temp_path)
            prompt = f"{theme_prompts[selected_theme]} {caption}"
            story = generate_story_from_text(prompt)
            
            # Clean up
            os.remove(temp_path)
        
        # Generate audio
        audio_filename = generate_audio_from_story(story)
        
        if audio_filename:
            audio_url = f"/audio/{audio_filename}"
        else:
            audio_url = None
        
        return jsonify({
            'story': story,
            'audioUrl': audio_url
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/audio/<filename>')
def serve_audio(filename):
    return send_file(
        os.path.join(app.config['AUDIO_FOLDER'], filename),
        mimetype='audio/mpeg'
    )

@app.route('/download-story', methods=['POST'])
def download_story():
    try:
        story = request.json.get('story')
        if not story:
            return jsonify({'error': 'No story provided'}), 400
            
        # Create temporary file
        temp_file = BytesIO()
        temp_file.write(story.encode())
        temp_file.seek(0)
        
        return send_file(
            temp_file,
            as_attachment=True,
            download_name='generated_story.txt',
            mimetype='text/plain'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)