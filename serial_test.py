
import serial
import asyncio
from serial.serialutil import SerialException
from winrt.windows.media.control import GlobalSystemMediaTransportControlsSessionManager as MediaManager
from time import sleep

# modified from https://blog.rareschool.com/2021/01/controlling-raspberry-pi-pico-using.html
class SerialSender:
    TERMINATOR = '\n'.encode('UTF8')

    def __init__(self, device='COM3', baud=115200, timeout=1):
        self.serial = serial.Serial(device, baud, timeout=timeout)

    def receive(self) -> str:
        line = self.serial.read_until(self.TERMINATOR)
        return line.decode('UTF8').strip()

    def send(self, text: str):
        line = '%s\n' % text
        self.serial.write(line.encode('UTF8'))

    def close(self):
        self.serial.close()

# https://stackoverflow.com/a/66037406
async def get_media_info():
    sessions = await MediaManager.request_async()

    # This source_app_user_model_id check and if statement is optional
    # Use it if you want to only get a certain player/program's media
    # (e.g. only chrome.exe's media not any other program's).

    # To get the ID, use a breakpoint() to run sessions.get_current_session()
    # while the media you want to get is playing.
    # Then set TARGET_ID to the string this call returns.

    current_session = sessions.get_current_session()
    if current_session:  # there needs to be a media session running
        info = await current_session.try_get_media_properties_async()

        # song_attr[0] != '_' ignores system attributes
        info_dict = {song_attr: info.__getattribute__(song_attr) for song_attr in dir(info) if song_attr[0] != '_'}

        # converts winrt vector to list
        info_dict['genres'] = list(info_dict['genres'])

        return info_dict


if __name__ == '__main__':

    previous_media_info = None
    
    while True:
        
        current_media_info = asyncio.run(get_media_info())
        
        if current_media_info != previous_media_info and current_media_info != None:
            print(current_media_info['title'])
            previous_media_info = current_media_info
            sleep(1)
            
            # recreate the serial each time to allow handling disconnection
            try:
                serial_sender = SerialSender()
                serial_sender.send(current_media_info['title'])
                serial_sender.close()
            except SerialException:
                pass
