# Danbooru Smart Downloader

The Danbooru Smart Downloader is a Python application that allows you to download images from Danbooru. Why is it smart?
1. It allows to download only certain images that match a specific tag.
2. Once an image is downloaded, it will not be downloaded again. Therefore, if you have a large collection of images you want to download, you can run the program multiple times and it will simply continue from there.
3. It stores the image, but also all the tags, and even all the available metadata, and stores everything in a comprehensive folder hierarchy.

## How to use

1. Install Python 3.10 or higher.
2. Install all dependencies using `pip install -r requirements.txt`.
3. Register on [Danbooru](https://danbooru.donmai.us/), go on your [profile](https://danbooru.donmai.us/profile) and generate an API key.
4. Run the script using `python danbooru_smart_downloader.py` and providing the needed arguments.

### Command arguments

* `--help`: Displays the help message.
* `--username <username>` and `--api_key <api_key>`: The username and API key to use to login to Danbooru. This method is actually not recommended. Prefer using the `--use_dotenv` instead.
* `--use_dotenv`: This command line argument allows you to a file to provide the username and API key. This is useful if you don't want to provide them as arguments every time you run the script. The file to create must be in the same directory thant the program. Its name must be `.env` and should look like this:
   ```dotenv
   NAME=<username>
   API_KEY=<api_key>
   ```
   **This file should not be shared with anyone, as an API key should be considered as sensitive as a password.**
* `--tag <tag>`: The tag to search for.
* `--limit <limit>`: The maximum number of images to download. If not specified, all available images will be downloaded. Note that not specifying a limit can result in a long download time.
* `--rating <rating>`: The rating of the images to download. Can be `g` (general), `q` (questionning), `s` (sensitive) or `e` (exlicit). If not specified, all ratings will be downloaded.

### Folder structure

All the images and corresponding informations are stored the following way:
```
images/
|   <tag 1>
|   |   <id 1>_image.<jpg/png/...>
|   |   <id 1>_tags.txt
|   |   <id 1>_infos.json
|   |   ...
|   <tag 2>
|   |   ...
|   ...
```

## How it works

When using the application, it checks all the images you have already downloaded for the corresponding tag. It then looks for the image with the largest ID and only downloads images with an ID larger than that. Using the `--ignore_existing` flag, this behavior is disabled, and the app starts looking for all images again. This can be useful when you accidentally delete part of the data since it allows you to "fill the gaps".