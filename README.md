# video_timecut
Cut video file into multiples subclips according to timecodes in and out stored in a csv file<br/>
Made by A.Mansat with Chat GPT 4.0<br/>

# csv file format<br/>
id;start_time;end_time<br/>
clip1;00:53:43;01:16:10<br/>
clip2;01:19:40;01:44:10<br/>


# timecode format: MM:SS/FPS 50<br/>

Change source code for time convertion:<br/>
def time_to_seconds(time_str, fps=50):#change fps value here according to your video file framerate<br/>
Add 1 seconde before and after via checkbox if needed<br/>

# Interface

![interface](https://github.com/user-attachments/assets/38b41141-56f0-4f4f-b2a0-f4380892e769)

# Process

![Python Video Cut (1)](https://github.com/user-attachments/assets/0de29bd8-2643-45cb-a907-34072df1397c)


