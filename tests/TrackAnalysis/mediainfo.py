
import pymediainfo

fileName = r"C:\Projects\Python\PySide\mkvbatchmultiplex\tests\MediaFiles\test\subs\ITA\Show Title - S01E01.ITA.ass"

info = pymediainfo.MediaInfo.parse(fileName, output="XML")

print(info)
