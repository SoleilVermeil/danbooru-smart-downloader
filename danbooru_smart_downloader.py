import os
import requests
import json
import argparse
import math
from tqdm import tqdm
import dotenv
import datetime
from multiprocessing import Pool, cpu_count

def login(username: str, api_key: str) -> None:
    """
    Logs in to the API using the given credentials.

    Parameters
    ----------
    * username (str): the username to login with
    * api_key (str): the api key to login with

    Returns
    -------
    None
    """
    print("Logging in...", end=" ")
    params = {
        'login': username,
        'api_key': api_key
    }
    response = requests.get(f"{base_url}/users.json", params=params)
    if response.status_code != 200:
        print(f"failed (status code: {response.status_code}).")
        print(response)
        exit(1)
    print("success!")

def unpack(args):
    """
    Unpacks the arguments and calls the function with the unpacked arguments.

    Parameters
    ----------
    * args (list): the arguments to unpack, where the first argument is the function to call
    """
    func = args[0]
    args = args[1:]
    return func(*args)

def download_image(info: dict, tag: str, verbose: bool = True) -> None:
    """
    Downloads the image and saves all its tags as well as all the image informations in files.

    Parameters
    ----------
    * info (dict): the image informations as a dictionary
    * tag (str): the tag to search for
    * verbose (bool): whether to print the progress or not

    Returns
    -------
    None
    """
    if verbose: print("Reading image informations...", end=" ")
    try:
        id = info['id']
        image_url = info['file_url']
        extension = info['file_ext']
        tags = info['tag_string']
        rating = info['rating']
    except KeyError:
        if verbose: print("ignored (wrong formatting).")
        return
    path = f"images/{tag}/{rating}"
    imagepath = f"{path}/{id}_image.{extension}"
    tagspath = f"{path}/{id}_tags.txt"
    jsonpath = f"{path}/{id}_infos.json"
    if os.path.exists(imagepath) and os.path.exists(tagspath) and os.path.exists(jsonpath):
        if verbose: print("ignored (already exists).")
        return
    if verbose: print(f"trying to download image with id '{id}'...", end=" ")
    if extension in ["mp4"]:
        if verbose: print("ignored (video).")
        return
    image_response = requests.get(image_url)
    image_data = image_response.content
    for chars in ["<", ">", ":", "\"", "\\", "|", "?", "*"]:
        while chars in path:
            path = path.replace(chars, "_")
        tag = tag.replace(chars, "_")
    if not os.path.exists(path):
        os.makedirs(path)
    with open(imagepath, "wb") as f:
        f.write(image_data)
    with open(tagspath, "w") as f:
        f.write("\n".join(tags.split(" ")))
    with open(jsonpath, "w") as f:
        json.dump(info, f, indent=4)
    if verbose: print("done!")

def get_images_infos(base_url: str, tag: str, limit: int | None = None, rating: str | None = None) -> list[dict]:
    """
    Makes a request to the API to get the informations of multiple images corresponding to the given tag. Images are sorted by ID, oldest first.

    Parameters
    ----------
    * base_url (str): the base URL of the API
    * tag (str): the tag to search for
    * limit (int | None): the maximum number of images to download if specified
    * rating (str | None): the rating of the images to download if specified

    Returns
    -------
    * (list[dict]): the informations of the images as a list of dictionaries
    """
    print("Requesting images infos...", end=" ")
    result = []
    max_items_per_page = 200
    if limit is None:
        limit = int(10e10)
    page_limit = math.ceil(limit / max_items_per_page)
    for page in range(1, page_limit + 1):
        max_items_for_current_page = max_items_per_page
        if page == page_limit:
            max_items_for_current_page = limit - max_items_per_page * (page_limit - 1)
        # TODO: improve the following line using for example requests.get(..., params=params)
        # NOTE: requests.get() automatically encodes the parameters, which is not wanted since a lot of tags contain special characters
        images_url = f"{base_url}/posts.json?"
        images_url += f"tags={tag}+order:id"
        if rating is not None:
            images_url += f"+rating:{rating}"
        images_url += "&"
        images_url += f"limit={max_items_for_current_page}&"
        images_url += f"page={page}&"
        response = requests.get(images_url)
        print(f"page '{images_url}'...", end=" ")
        if response.status_code != 200:
            print(f"failed (status code: {response.status_code}).")
            continue
        items = response.json()
        if len(items) == 0:
            break
        result += items
    print(f"{len(result)} images found!")
    return result

if __name__ == "__main__":
    
    # Configuring the commands

    parser = argparse.ArgumentParser(description='Downloads images from danbooru')
    parser.add_argument('--use_dotenv', action='store_true', help='use .env file', required=False)
    parser.add_argument('--username', type=str, help='username to login with', required=False)
    parser.add_argument('--api_key', type=str, help='api key to login with', required=False)
    parser.add_argument('--tag', type=str, help='tag to search for', required=True)
    parser.add_argument('--limit', type=int, help='maximum number of images to download if specified', required=False)
    parser.add_argument('--rating', choices=['g', 'q', 's', 'e'], help='rating of the images to download if specified', required=False)

    # Loading the credentials

    if parser.parse_args().use_dotenv and (parser.parse_args().username is None and parser.parse_args().api_key is None):
        dotenv.load_dotenv()
        username = os.getenv("NAME")
        api_key = os.getenv("API_KEY")
    elif (parser.parse_args().username is not None and parser.parse_args().api_key is not None) and not parser.parse_args().use_dotenv:
        username = parser.parse_args().username
        api_key = parser.parse_args().api_key
    else:
        print("ERROR: either use --use_dotenv or both --username and --api_key")
        exit(1)
    
    # Setting the base URL

    base_url = "https://danbooru.donmai.us"
    
    # Connecting to the API
    
    timer = datetime.datetime.now()
    login(username, api_key)
    # print(f"Elapsed time: {datetime.datetime.now() - timer}")

    # Flushing credentials

    username = None
    api_key = None
    
    # Requesting the images

    tag = parser.parse_args().tag

    timer = datetime.datetime.now()
    kwargs = {"tag": tag, "base_url": base_url}
    if parser.parse_args().rating is not None:
        kwargs["rating"] = parser.parse_args().rating
    if parser.parse_args().limit is not None:
        kwargs["limit"] = parser.parse_args().limit
    
    infos = get_images_infos(**kwargs)
    # print(f"Elapsed time: {datetime.datetime.now() - timer}")

    # Downloading the images

    timer = datetime.datetime.now()
    with Pool(processes=cpu_count()) as pool:
        with tqdm(total=len(infos)) as pbar:
            for _ in pool.imap_unordered(unpack, [(download_image, info, tag, False) for info in infos]):
                pbar.update()
    # print(f"Elapsed time: {datetime.datetime.now() - timer}")
