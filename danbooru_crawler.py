import os
import requests
import json
import argparse
import glob
import math

# Configuring the commands

parser = argparse.ArgumentParser(description='Downloads images from danbooru')
parser.add_argument('--username', type=str, help='username to login with', required=True)
parser.add_argument('--api_key', type=str, help='api key to login with', required=True)
parser.add_argument('--tag', type=str, help='tag to search for', required=True)
parser.add_argument('--limit', type=int, help='maximum number of images to download', required=True)
parser.add_argument('--force_download', type=bool, help='force download even if image already exists', required=False, default=False)
parser.add_argument('--test', action='store_true', help='use testbooru instead of danbooru', required=False)

# Setting the base URL

url_danbooru = "https://danbooru.donmai.us"
url_testbooru = "https://testbooru.donmai.us"
base_url = url_danbooru if not parser.parse_args().test else url_testbooru

# Login to Danbooru

print("Logging in to Danbooru...", end=" ")
login_url = f"{base_url}/profile.json?login={parser.parse_args().username}&api_key={parser.parse_args().api_key}"
try:
    response = requests.get(login_url)
    response.raise_for_status()
except requests.exceptions.RequestException as e:
    print(f"failed")
    exit(1)
print("success")

# Get the tag

tag = parser.parse_args().tag

# Get the largest id already downloaded

files = glob.glob(f"images/{tag}/*/*_infos.json", recursive=True)
ids = [int(os.path.basename(f).split("_")[0]) for f in files]
if len(ids) > 0:
    id_max = max(ids)
else:
    id_max = 0

# Get images
# NOTE: Since Danbooru limits the number of images per page to 200, we need to get the images page by page.

print("Getting images...")
per_page_max = 20
page_limit = math.ceil(parser.parse_args().limit / per_page_max)

for page in range(1, page_limit + 1):
    
    # Determine the number of images to get for the ongoing request
    
    per_page_current = per_page_max
    if page == page_limit:
        per_page_current = parser.parse_args().limit - per_page_max * (page_limit - 1)
    images_url = f"{base_url}/posts.json?tags={tag}+order:id+id:>{id_max}&limit={per_page_current}&page={page}"
    
    # Go through the images
    
    try:
        
        response = requests.get(images_url)
        response.raise_for_status()
        images_data = response.json()

        # Check if there are no more results
        
        if not images_data:
            print("No more results.")
            break

        # Save the images
        
        for i, image in enumerate(images_data):
            
            progress = f"[{(i + 1) + (page - 1) * per_page_max:>4}/{parser.parse_args().limit:>4}]"
            print(f"{progress} Downloading image {image['id']}...", end=" ")
            
            try:
                
                id = image['id']
                image_url = image['file_url']
                ext = image['file_ext']
                tags = image['tag_string']
                rating = image['rating']
                
                if ext in ["mp4"]:
                    print("ignored (video)")
                    continue
                
                # Save the image
                image_response = requests.get(image_url)
                image_response.raise_for_status()
                image_data = image_response.content
                
                path = f"images/{tag}/{rating}"
                imagepath = f"{path}/{id}_image.{ext}"
                tagspath = f"{path}/{id}_tags.txt"
                jsonpath = f"{path}/{id}_infos.json"
                
                if not os.path.exists(path):
                    os.makedirs(path)
                    
                if not parser.parse_args().force_download:
                    if os.path.exists(imagepath) and os.path.exists(tagspath) and os.path.exists(jsonpath):
                        print("ignored (already exists)")
                        continue
                
                with open(imagepath, "wb") as f:
                    f.write(image_data)
                    
                with open(tagspath, "w") as f:
                    f.write("\n".join(tags.split(" ")))
                    
                with open(jsonpath, "w") as f:
                    json.dump(image, f, indent=4)
                
                print("done")
                
            except KeyError:
                continue
    except requests.exceptions.RequestException as e:
        print(f"An error occured while trying to access {images_url}.")
        continue
    
print("Done!")