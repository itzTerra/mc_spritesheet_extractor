from PIL import Image
import re
from typing import Dict, List, Tuple

from django_slugify import slugify


# Read the coordinates from the text file
def readCoords(path: str, item_name = "all", print_debug = False) -> List[Dict]:
    coordinates = []
    with open(path, "r") as file:
        for line in file:
            line = line.strip()
            if not line:
                continue
            
            parts = line.split("\t")
            name = parts[0]
            if item_name != "all" and not re.match(item_name, name):
                continue
            
            params = {}
            for param in parts[1:]:
                key, value = param.split("=")
                params[key] = int(value)
            coordinates.append({"name": name, **params})
    
    if print_debug:
        # Display the extracted coordinates
        for coord in coordinates:
            print(coord)
    
    return coordinates


# Extract each image from the sprite sheet
def extractImages(spritesheet: Image.Image, coords: List[Dict]) -> Dict[str, Image.Image]:
    images = {}
    for coord in coords:
        name = coord["name"]
        x, y, w, h = coord["x"], coord["y"], coord["w"], coord["h"]
        
        # Crop the image based on the coordinates
        images[name] = spritesheet.crop((x, y, x + w, y + h))
    
    return images


def recolorImages(images: Dict[str, Image.Image], tintColor: Tuple[int]) -> None:
    for image in images.values():
        # Get the pixel data
        pixels = image.load()

        # Iterate over each pixel and change the color
        for i in range(image.width):
            for j in range(image.height):
                current_color = pixels[i, j]
                if current_color[3] != 0:  # Exclude fully transparent pixels
                    pixels[i, j] = tintColor
    


def saveImages(images: Dict[str, Image.Image]) -> None:
    for name, image in images.items():
        # Save the extracted image
        image.save(f"output/{slugify(name)}.png")
    print(f"Saved {len(images)} image(s)")


# ===================================== EXAMPLE ==========================================

if __name__ == "__main__":
    SPRITESHEET_PATH = "input/minecraft_textures_atlas_particles.png_0.png"
    COORDS_PATH = "input/minecraft_textures_atlas_particles.png.txt"

    TEAL = (106, 210, 178)

    # Load the sprite sheet image
    spritesheet = Image.open(SPRITESHEET_PATH)

    coordinates = readCoords(COORDS_PATH, r"minecraft:glitter_[0-9]+")
    images = extractImages(spritesheet, coordinates)
    recolorImages(images, TEAL)
    saveImages(images)