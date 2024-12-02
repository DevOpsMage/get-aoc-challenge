#!/usr/bin/env python3

import requests
import datetime
import os
import sys
import time
import subprocess
from bs4 import BeautifulSoup
import html2text
import argparse

# Import rookiepy for cookie retrieval
import rookiepy


def fetch_day(year, day, session_cookie, parent_dir):
    cookies = {"session": session_cookie}

    # Prepare URLs
    base_url = f"https://adventofcode.com/{year}/day/{day}"
    description_url = base_url
    input_url = f"{base_url}/input"

    # Fetch the challenge description
    response = requests.get(description_url, cookies=cookies)
    if response.status_code == 200:
        pass  # Successful request
    elif response.status_code == 400:
        print(f"Day {day}: Bad request. The server didn't understand the request.")
        return False
    elif response.status_code == 404:
        print(f"Day {day}: Challenge not found. It may not be available yet.")
        return False
    elif response.status_code == 500:
        print(f"Day {day}: Server error. Try again later.")
        return False
    elif response.status_code == 401:
        print(f"Day {day}: Unauthorized. Invalid or expired session cookie.")
        return False
    else:
        print(
            f"Day {day}: Error fetching the challenge description: {response.status_code}"
        )
        return False

    soup = BeautifulSoup(response.content, "html.parser")
    # Find the article with class 'day-desc'
    articles = soup.find_all("article", class_="day-desc")

    if not articles:
        print(
            f"Day {day}: Challenge not available yet or unable to find challenge description."
        )
        return False

    # Combine the contents of all articles (some days have two parts)
    content = "\n".join(str(article) for article in articles)

    # Convert HTML to Markdown
    h = html2text.HTML2Text()
    h.ignore_links = False
    markdown = h.handle(content)

    # Fetch the puzzle input
    input_response = requests.get(input_url, cookies=cookies)
    if input_response.status_code == 200:
        puzzle_input = input_response.text.strip()
    elif input_response.status_code == 404:
        print(f"Day {day}: Puzzle input not found.")
        puzzle_input = ""
    elif input_response.status_code == 401:
        print(f"Day {day}: Unauthorized. Invalid or expired session cookie.")
        return False
    else:
        print(
            f"Day {day}: Error fetching the puzzle input: {input_response.status_code}"
        )
        return False

    # Prepare the output directories
    year_dir = os.path.join(parent_dir, str(year))
    os.makedirs(year_dir, exist_ok=True)

    # Create day directory inside the year directory
    day_dir_name = f"Day-{day:02d}"
    day_dir = os.path.join(year_dir, day_dir_name)
    os.makedirs(day_dir, exist_ok=True)

    # Save the markdown file in the day directory
    filename_md = f"Day{day:02d}.md"
    file_path_md = os.path.join(day_dir, filename_md)
    with open(file_path_md, "w", encoding="utf-8") as f:
        f.write(markdown)

    # Save the puzzle input in the same day directory
    filename_input = f"Day{day:02d}_input.txt"
    file_path_input = os.path.join(day_dir, filename_input)
    with open(file_path_input, "w", encoding="utf-8") as f:
        f.write(puzzle_input)

    print(f"Day {day}: Challenge and input saved to {day_dir}")
    return True


def get_session_cookie():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    session_file = os.path.join(script_dir, "session.txt")

    # Check if session.txt exists
    if os.path.exists(session_file):
        with open(session_file, "r") as f:
            session_cookie = f.read().strip()
            if session_cookie:
                return session_cookie

    print("session.txt file with your session cookie is missing or empty.")

    # Prompt user to select their browser
    browsers = [
        "Arc",
        "Brave",
        "Cachy",
        "Chrome",
        "Chromium",
        "Edge",
        "Firefox",
        "Internet Explorer",
        "LibreWolf",
        "Opera",
        "Opera GX",
        "Safari",
        "Vivaldi",
        "Zen",
    ]

    print("Attempting to retrieve session cookie from your browser using rookiepy.")
    print("Please select your browser:")
    for idx, browser in enumerate(browsers, 1):
        print(f"{idx}. {browser}")
    choice = input("Enter the number corresponding to your browser (e.g., 1): ")

    try:
        choice = int(choice)
        if choice < 1 or choice > len(browsers):
            raise ValueError
        browser_name = browsers[choice - 1]
    except ValueError:
        print("Invalid selection. Unable to retrieve session cookie automatically.")
        return prompt_for_session_cookie(session_file)

    # Attempt to get cookies from the selected browser
    try:
        # Define function to call based on browser name
        if browser_name == "Arc":
            cookies = rookiepy.arc(["adventofcode.com"])
        elif browser_name == "Brave":
            cookies = rookiepy.brave(["adventofcode.com"])
        elif browser_name == "Cachy":
            cookies = rookiepy.cachy(["adventofcode.com"])
        elif browser_name == "Chrome":
            cookies = rookiepy.chrome(["adventofcode.com"])
        elif browser_name == "Chromium":
            cookies = rookiepy.chromium(["adventofcode.com"])
        elif browser_name == "Edge":
            cookies = rookiepy.edge(["adventofcode.com"])
        elif browser_name == "Firefox":
            cookies = rookiepy.firefox(["adventofcode.com"])
        elif browser_name == "Internet Explorer":
            cookies = rookiepy.ie(["adventofcode.com"])
        elif browser_name == "LibreWolf":
            cookies = rookiepy.librewolf(["adventofcode.com"])
        elif browser_name == "Opera":
            cookies = rookiepy.opera(["adventofcode.com"])
        elif browser_name == "Opera GX":
            cookies = rookiepy.operagx(["adventofcode.com"])
        elif browser_name == "Safari":
            cookies = rookiepy.safari(["adventofcode.com"])
        elif browser_name == "Vivaldi":
            cookies = rookiepy.vivaldi(["adventofcode.com"])
        elif browser_name == "Zen":
            cookies = rookiepy.zen(["adventofcode.com"])
        else:
            print("Unsupported browser selected.")
            return prompt_for_session_cookie(session_file)

        # Find the 'session' cookie
        session_cookie = None
        for cookie in cookies:
            print(cookie)
            if cookie["name"] == "session":
                session_cookie = cookie["value"]
                break

        if session_cookie:
            # Save to session.txt
            with open(session_file, "w") as f:
                f.write(session_cookie)
            print("Session cookie retrieved and saved to session.txt.")
            return session_cookie
        else:
            print("Session cookie not found in browser cookies.")
            return prompt_for_session_cookie(session_file)

    except Exception as e:
        error_message = str(e).lower()
        if "admin" in error_message or "permission" in error_message:
            print(f"Permission error while accessing browser cookies: {e}")
            response = (
                input(
                    "Do you want to rerun the script with administrative privileges? (yes/no): "
                )
                .strip()
                .lower()
            )
            if response in ["yes", "y"]:
                run_as_admin()
            else:
                print("Cannot proceed without necessary permissions.")
                sys.exit(1)
        else:
            print(f"An error occurred while retrieving cookies: {e}")
            return prompt_for_session_cookie(session_file)


def prompt_for_session_cookie(session_file):
    print("Automated attempt to retrieve the session cookie was unsuccessful.")
    session_cookie = input("Please enter your session cookie value: ").strip()
    if session_cookie:
        with open(session_file, "w") as f:
            f.write(session_cookie)
        print("Session cookie saved to session.txt.")
        return session_cookie
    else:
        print("No session cookie provided. Exiting.")
        sys.exit(1)


def run_as_admin():
    """Relaunch the script with administrative privileges."""
    print("Attempting to relaunch the script with administrative privileges...")

    try:
        if sys.platform.startswith("win"):
            # Windows
            import ctypes

            script = os.path.abspath(__file__)
            params = " ".join(f'"{arg}"' if " " in arg else arg for arg in sys.argv[1:])
            # ShellExecuteW returns >32 if successful
            result = ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, f'"{script}" {params}', None, 1
            )
            if result <= 32:
                print("Failed to elevate privileges.")
                sys.exit(1)
            else:
                sys.exit(0)  # The elevated process will take over
        else:
            # Unix-like systems
            script = os.path.abspath(__file__)
            params = " ".join(sys.argv[1:])
            # Check if already running as root
            if os.geteuid() == 0:
                print("Already running with administrative privileges.")
                return
            else:
                # Relaunch with sudo
                try:
                    os.execvp("sudo", ["sudo", sys.executable, script] + sys.argv[1:])
                except Exception as e:
                    print(f"Failed to elevate privileges: {e}")
                    sys.exit(1)
    except Exception as e:
        print(f"Failed to relaunch as admin: {e}")
        sys.exit(1)


def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Fetch Advent of Code challenge and input."
    )
    parser.add_argument(
        "--year",
        type=int,
        help="Year of the Advent of Code event (default: current year)",
    )
    parser.add_argument(
        "--day", type=int, help="Day of the challenge (default: current day)"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Fetch all available days for the specified year",
    )
    args = parser.parse_args()

    # Use provided year or current year
    if args.year:
        year = args.year
    else:
        year = datetime.datetime.now().year

    # Load session cookie
    session_cookie = get_session_cookie()

    # Prepare the output directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.abspath(os.path.join(script_dir, os.pardir))

    if args.all:
        if args.day:
            print("Cannot use --day and --all together. Please choose one.")
            return
        # Fetch all days
        for day in range(1, 26):  # Advent of Code has 25 days
            success = fetch_day(year, day, session_cookie, parent_dir)
            if not success:
                print(f"Day {day}: Skipping due to previous error.")
            # Optional: Sleep between requests to be courteous to the server
            time.sleep(1)
    else:
        # Use provided day or current day
        if args.day:
            day = args.day
        else:
            today = datetime.datetime.now()
            if today.month != 12:
                print("Advent of Code is only in December!")
                return
            day = today.day

        # Fetch the specified day
        success = fetch_day(year, day, session_cookie, parent_dir)
        if not success and "session.txt" in locals():
            # Invalid session cookie, prompt user to update it
            print("Your session cookie may be invalid or expired.")
            os.remove(os.path.join(script_dir, "session.txt"))
            session_cookie = get_session_cookie()
            fetch_day(year, day, session_cookie, parent_dir)


if __name__ == "__main__":
    main()
