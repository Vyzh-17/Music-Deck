import asyncio
import time
import serial

from winsdk.windows.media.control import (
    GlobalSystemMediaTransportControlsSessionManager
)


# --------------------------------------------------
# SETTINGS
# --------------------------------------------------

ARDUINO_PORT = "COM5"
BAUD_RATE = 9600

UPDATE_INTERVAL = 1


# --------------------------------------------------
# GET CURRENTLY PLAYING MUSIC
# --------------------------------------------------

async def get_current_music():
    try:
        manager = await (
            GlobalSystemMediaTransportControlsSessionManager
            .request_async()
        )

        session = manager.get_current_session()

        if session is None:
            return None, None

        properties = await session.try_get_media_properties_async()

        title = properties.title
        artist = properties.artist

        if not title:
            title = "Unknown Song"

        if not artist:
            artist = "Unknown Artist"

        return title, artist

    except Exception as error:
        print("Media detection error:", error)

        return None, None


# --------------------------------------------------
# SEND MUSIC INFORMATION TO ARDUINO
# --------------------------------------------------

def send_music(arduino, title, artist):
    message = title + "|" + artist + "\n"

    arduino.write(message.encode("utf-8"))

    print("Sent to Arduino:")
    print("Song  :", title)
    print("Artist:", artist)
    print()


# --------------------------------------------------
# MAIN PROGRAM
# --------------------------------------------------

async def main():

    print("--------------------------------")
    print("       MUSIC DECK")
    print("--------------------------------")
    print()

    print("Connecting to Arduino...")

    try:
        arduino = serial.Serial(
            ARDUINO_PORT,
            BAUD_RATE,
            timeout=1
        )

    except Exception as error:
        print()
        print("Could not connect to Arduino.")
        print("Check the COM port.")
        print()
        print("Error:", error)

        return

    # Opening the serial connection normally resets
    # an Arduino Uno, so give it time to restart.

    time.sleep(2)

    print("Arduino connected!")
    print()
    print("Waiting for music...")
    print()

    previous_title = ""
    previous_artist = ""

    try:

        while True:

            title, artist = await get_current_music()

            if title is not None and artist is not None:

                if (
                    title != previous_title
                    or artist != previous_artist
                ):

                    send_music(
                        arduino,
                        title,
                        artist
                    )

                    previous_title = title
                    previous_artist = artist

            else:

                if previous_title != "":

                    send_music(
                        arduino,
                        "No Music",
                        "Playing"
                    )

                    previous_title = ""
                    previous_artist = ""

            await asyncio.sleep(UPDATE_INTERVAL)

    except KeyboardInterrupt:

        print()
        print("Music Deck stopped.")

    finally:

        arduino.close()


# --------------------------------------------------
# START PROGRAM
# --------------------------------------------------

if __name__ == "__main__":
    asyncio.run(main())