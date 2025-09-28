import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.services.image_generator import ImageGenerator

# Test the pose functionality
generator = ImageGenerator()
product_data = {
    'Description': 'Elegant evening gown', 
    'Occasion': 'wedding', 
    'Gender': 'women', 
    'RecommendedPoses': ['standing straight with hands clasped', 'sitting gracefully']
}
prompt = generator._create_generation_prompt(product_data, 'elegant ballroom', '9:16', 'women')
print('POSE INSTRUCTION:')
lines = prompt.split('\n')
for line in lines:
    if 'Position model' in line:
        print(line)