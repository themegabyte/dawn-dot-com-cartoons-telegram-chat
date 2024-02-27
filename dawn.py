# %%
import requests
from bs4 import BeautifulSoup
from telegram import Bot
import asyncio
import sys

# %%

if len(sys.argv) < 3:
    print("Usage: python script.py BOT_TOKEN CHAT_ID")
    exit(1)

# BOT_TOKEN = ""

# # Replace with the chat ID you want to send the image to
# CHAT_ID = ""

BOT_TOKEN = sys.argv[1]
CHAT_ID = sys.argv[2]

bot = Bot(token=BOT_TOKEN)


def get_cartoon_href(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find the anchor tag with the specific title attribute
    targeted_link = soup.find(
        'a', title=lambda title: title is not None and title.startswith("Cartoon: "))

    # Extract the href attribute
    if targeted_link:
        href_value = targeted_link.get('href')
        return href_value
    else:
        print("No link with the specified title attribute found.")

# %%


def get_cartoon_title_and_link(href):
    if href:
        try:
            response = requests.get(href)
            response.raise_for_status()  # Raise an exception for error status codes

            soup = BeautifulSoup(response.text, 'html.parser')
            image_element = soup.select_one("div.media__item > picture > img")

            if image_element:
                src = image_element.get('src')
                title = image_element.get('title')
                print(f"Image src: {src}")
                print(f"Image title: {title}")
                return {'src': src, 'title': title}
            else:
                print("Image element not found using the provided selector.")
        except requests.exceptions.RequestException as e:
            print(f"An error occurred while fetching the href: {e}")
    else:
        print("href not found or not provided.")

# %%


def download_image(href, filename):
    if href:
        try:
            # Fetch image content
            image_response = requests.get(href, stream=True)
            image_response.raise_for_status()  # Raise an exception for error status codes

            # Download and save image
            with open(filename + ".jpg", "wb") as f:
                for chunk in image_response.iter_content(1024):
                    f.write(chunk)

            # Proceed with parsing remaining content from href ...

        except requests.exceptions.RequestException as e:
            print(f"An error occurred while fetching the image: {e}")
    else:
        print("href not found or not provided.")

# %%


async def send_to_telegram(filename, caption):
    # Replace with your bot's token
    try:
        with open(filename, "rb") as f:
            # Send the image to the chat
            await bot.send_photo(chat_id=CHAT_ID, photo=f, caption=caption)
        try:
            import os
            os.remove(filename)
        except FileNotFoundError:
            print("Downloaded image not found to be deleted.")
        return True
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False


# %%


async def main():
    url = "https://www.dawn.com/"

    try:
        # Send a GET request to the website
        response = requests.get(url)

        # Check if request was successful (status code 200)
        if response.status_code == 200:
            # Get the HTML content
            html_content = response.text
            cartoon_href = get_cartoon_href(html_content)
            title_and_link_dict = get_cartoon_title_and_link(cartoon_href)
            print(title_and_link_dict)
            download_image(
                href=title_and_link_dict["src"], filename=title_and_link_dict["title"])
            success = await send_to_telegram(title_and_link_dict["title"] + ".jpg", caption=cartoon_href)
            if not success:
                await bot.send_message(chat_id=CHAT_ID, text="Unable to scrape")
        else:
            print("Failed to retrieve the website content.")
    except Exception as e:
        print(f"An error occurred: {e}")

asyncio.run(main())
