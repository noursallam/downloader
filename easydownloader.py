import yt_dlp

link = input("Enter the YouTube playlist URL: ")

yt_dlp.YoutubeDL({'format': 'best', 'outtmpl': '%(playlist_title)s/%(title)s.%(ext)s'}).download([link])
