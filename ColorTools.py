from sklearn.cluster import KMeans
import numpy as np
import colorsys

def rgb_to_hex(rgb):
    """Convert RGB tuple to hex color string"""
    return '#{:02x}{:02x}{:02x}'.format(rgb[0], rgb[1], rgb[2])

def get_dominant_colors(image, num_colors=5):
    """Extract dominant colors from an image using K-means clustering, sorted by visual appearance"""
    # Convert image to RGB if it isn't already
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # Resize image for faster processing
    image = image.resize((150, 150))
    
    # Convert image to numpy array
    data = np.array(image)
    data = data.reshape((-1, 3))
    
    # Use K-means to find dominant colors
    kmeans = KMeans(n_clusters=num_colors, random_state=42, n_init=10)
    kmeans.fit(data)
    
    # Get the colors and labels
    colors = kmeans.cluster_centers_.astype(int)
    labels = kmeans.labels_
    
    # Convert RGB to HSV for better sorting
    def rgb_to_hsv(r, g, b):
        r, g, b = r/255.0, g/255.0, b/255.0
        max_val = max(r, g, b)
        min_val = min(r, g, b)
        diff = max_val - min_val
        
        # Hue calculation
        if diff == 0:
            h = 0
        elif max_val == r:
            h = (60 * ((g - b) / diff) + 360) % 360
        elif max_val == g:
            h = (60 * ((b - r) / diff) + 120) % 360
        else:
            h = (60 * ((r - g) / diff) + 240) % 360
        
        # Saturation calculation
        s = 0 if max_val == 0 else diff / max_val
        
        # Value (brightness) calculation
        v = max_val
        
        return h, s, v
    
    # Create sorting key: sort by hue first, then brightness (low to high)
    def color_sort_key(color):
        r, g, b = color
        h, s, v = rgb_to_hsv(r, g, b)
        # Sort by hue first, then by brightness (low to high)
        return (h, v)
    
    # Sort colors by visual appearance
    sorted_colors = sorted(colors, key=color_sort_key)
    
    # Convert to hex
    hex_colors = [rgb_to_hex(tuple(color)) for color in sorted_colors]
    
    return hex_colors



def extract_color_palette(image, num_colors: int):
    # Convert to RGB if not already (handles RGBA, grayscale, etc.)
    image = image.resize((150, 150))
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # Convert image to numpy array
    image_array = np.array(image)
    
    # Reshape the image to be a list of pixels
    pixels = image_array.reshape((-1, 3))
    
    # Apply K-means clustering to find dominant colors
    kmeans = KMeans(n_clusters=num_colors, random_state=69, n_init=10)
    kmeans.fit(pixels)
    
    # Get the cluster centers (these are our palette colors)
    colors = kmeans.cluster_centers_
    
    # Convert to hex codes
    hex_colors = []
    for color in colors:
        # Convert to integers and ensure they're in valid RGB range
        r, g, b = [int(c) for c in np.clip(color, 0, 255)]
        hex_color = f"#{r:02x}{g:02x}{b:02x}"
        hex_colors.append(hex_color)
    
    # Sort colors by hue first, then brightness
    def sort_by_hue_brightness(hex_color):
        # Convert hex to RGB
        r = int(hex_color[1:3], 16) / 255.0
        g = int(hex_color[3:5], 16) / 255.0
        b = int(hex_color[5:7], 16) / 255.0
        
        # Convert RGB to HSV to get hue
        h, s, v = colorsys.rgb_to_hsv(r, g, b)
        
        # For very low saturation (grays), treat as special case and sort by brightness only
        if s < 0.1:
            return (1000, v)  # Put grays at end, sorted by brightness
        
        # For colored pixels, sort by hue first, then brightness
        return (h, v)
    
    hex_colors.sort(key=sort_by_hue_brightness)
    
    return hex_colors