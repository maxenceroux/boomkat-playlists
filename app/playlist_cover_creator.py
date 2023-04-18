import requests
from PIL import Image
import os
import math


class CoverGenerator:
    def __init__(self) -> None:
        pass

    def download_image(self, url):
        response = requests.get(url)
        response.raise_for_status()
        return response.content

    def average_image_color(self, image_file):

        # Open image and get its pixels
        with Image.open(image_file) as img:
            pixels = img.load()
            width, height = img.size

            # Calculate the average color tone
            avg_color = (0, 0, 0)
            try:
                for y in range(height):
                    for x in range(width):
                        avg_color = tuple(
                            map(sum, zip(avg_color, pixels[x, y]))
                        )
                avg_color = tuple(x // (width * height) for x in avg_color)
            except:
                avg_color = (127, 127, 127)

            return avg_color

    def order_images_by_tone(self, image_urls):
        # Download and save images to a temporary file
        image_files = []
        for url in image_urls:
            image_data = self.download_image(url)

            with open(f"{url.split('/')[-1]}.jpg", "wb") as f:
                f.write(image_data)
            image_files.append(f"{url.split('/')[-1]}.jpg")

        # Get average color tone for each image
        image_colors = [
            (image, self.average_image_color(image)) for image in image_files
        ]

        # Order the images by average color tone
        ordered_images = [
            image
            for (image, color) in sorted(image_colors, key=lambda x: sum(x[1]))
        ]
        return ordered_images

    def create_playlist_cover(self, image_urls, merge_item_path):
        ordered_images = self.order_images_by_tone(image_urls)
        # Determine the size of the square that will contain the ordered images
        size = int(math.trunc(math.sqrt(len(ordered_images))))

        # Create a single image that contains the ordered images in a square
        total_width = 400
        total_height = 400
        result_image = Image.new(
            "RGB", (total_width, total_height), (255, 255, 255)
        )
        x_offset = 0
        y_offset = 0
        for image in ordered_images:
            if image is None:
                continue
            with Image.open(image) as img:
                img = img.resize((total_width // size, total_height // size))
                result_image.paste(img, (x_offset, y_offset))
                x_offset += total_width // size
                if x_offset >= total_width:
                    x_offset = 0
                    y_offset += total_height // size
            if os.path.isfile(image):
                os.remove(image)
        merge_image = Image.open(merge_item_path)
        merge_image.paste(result_image, (50, 50))
        merge_image = merge_image.convert("RGB")
        return merge_image
