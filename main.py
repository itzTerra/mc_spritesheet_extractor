from PIL import Image
import re
import os
from typing import Dict, List, Tuple

from django_slugify import slugify


def readCoords(path: str, item_name = "all", print_debug = False) -> List[Dict]:
    """
    Read the coordinates from the text file, based on name

    item_name -- regex or "all", empty string "" defaults to all
    """
    
    coordinates = []
    with open(path, "r") as file:
        for line in file:
            line = line.strip()
            if not line:
                continue
            
            parts = line.split("\t")
            name = parts[0]
            if (item_name != "all" or item_name != "") and not re.match(item_name, name):
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


# Extract each image from the spritesheet
def extractImages(spritesheet: Image.Image, coords: List[Dict]) -> Dict[str, Image.Image]:
    images = {}
    for coord in coords:
        name = coord["name"]
        x, y, w, h = coord["x"], coord["y"], coord["w"], coord["h"]
        
        # Crop the image based on the coordinates
        images[name] = spritesheet.crop((x, y, x + w, y + h))
    
    return images


def recolorImages(images: List[Image.Image], tintColor: Tuple[int]) -> None:
    for image in images:
        # Get the pixel data
        pixels = image.load()

        # Iterate over each pixel and change the color
        for i in range(image.width):
            for j in range(image.height):
                current_color = pixels[i, j]
                if current_color[3] != 0:  # Exclude fully transparent pixels
                    pixels[i, j] = tintColor
    

def saveImages(images: Dict[str, Image.Image], output_dir = "output/", new_name = "") -> None:
    """
    new_name -- specify the name of images to which the index gets appended, defaults to existing names
    """
    # Create the output folder if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Save the extracted images
    if new_name:    
        for i, image in enumerate(images.values()):
            image.save(f"{output_dir}{new_name}{i}.png")
    else:
        for name, image in images.items():
            image.save(f"{output_dir}{slugify(name)}.png")
    
    print(f"Saved {len(images)} image(s)")


def createTexture(images: List[Image.Image], output_path = "output/texture.png") -> None:
    # Create the output folder if it doesn't exist
    output_dir = os.path.dirname(output_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Open the first image to get the dimensions
    width, height = images[0].size
    
    # Create a blank canvas for the combined image
    combined_image = Image.new('RGBA', (width, height * len(images)))
    
    # Iterate through the images and paste them onto the combined image
    for i, image in enumerate(images):
        combined_image.paste(image, (0, i * height))
    
    # Save the combined image
    combined_image.save(output_path)
    
    print(f"Texture saved as {output_path}")


# ===================================== EXAMPLE ==========================================

if __name__ == "__main__":
    SPRITESHEET_PATH = "input/minecraft_textures_atlas_particles.png_0.png"
    COORDS_PATH = "input/minecraft_textures_atlas_particles.png.txt"
    
    COORDS_NAME = r"minecraft:glitter_[0-9]+"

    TEAL = (106, 210, 178)

    # Load the sprite sheet image
    spritesheet = Image.open(SPRITESHEET_PATH)

    coordinates = readCoords(COORDS_PATH, COORDS_NAME)
    images = extractImages(spritesheet, coordinates)
    recolorImages(images.values(), TEAL)
    saveImages(images, new_name="wisp_glitter")
    createTexture(list(images.values()), "output/wisp_glitter.png")