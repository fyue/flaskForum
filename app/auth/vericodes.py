import os, random, hashlib, ipdb
from PIL import Image, ImageFont, ImageDraw, ImageFilter
from datetime import datetime
from random import seed
from flask import current_app

def generate_verification_code():
    """random nums or letters"""
    def rndChar():
        letterNum = random.randint(65, 90)
        numNum = random.randint(48, 57)
        letter_num = [letterNum, numNum]
        random.shuffle(letter_num)
        return chr(letter_num[0])
    
    """random color1"""
    def rndColor():
        return (random.randint(128, 255), random.randint(128, 255), \
                random.randint(128, 255))
    
    """random color12"""
    def rndColor2():
        return (random.randint(32, 127), random.randint(32, 127), \
                random.randint(32, 127))
    
    """80 x 20"""
    width = 20 * 4
    height = 30
    image = Image.new("RGB", (width, height), (255, 255, 255))
    
    """create Font instance"""
    fontPath = current_app.config["FLASKY_VERIFIED_FONT"]
    font = ImageFont.truetype(fontPath, 24)
    
    """create Draw instance"""
    draw = ImageDraw.Draw(image)
    
    """fill each pixel"""
    for x in range(width):
        for y in range(height):
            draw.point((x, y), fill=rndColor2())
    
    """output each words"""
    tmpList = []
    for t in range(4):
        seed()
        eachChar = rndChar()
        draw.text((16 * t + 8, 5), eachChar, font = font, \
                  fill=rndColor())
        tmpList.append(eachChar)

    """blur it!"""
    image = image.filter(ImageFilter.SMOOTH_MORE)
    
    """create verification_code"""
    codeChar = tmpList[0]+tmpList[1]+tmpList[2]+tmpList[3]
    
    """create pichashname"""
    md5 = hashlib.md5()
    md5.update(str(datetime.utcnow()).encode("utf-8"))
    Hash = str(md5.hexdigest())
    codeHashName =Hash + ".jpg"
    
    """create pic_output dir_path"""
    current_dir = os.path.abspath(os.path.dirname(__file__))
    outputDir = os.path.join(os.path.split(current_dir)[0], \
                              "static/verifyCode")
    if not os.path.isdir(outputDir):
        os.mkdir(outputDir)
        
    """save the Vpic"""
    image.save(outputDir + "/" + codeHashName, "jpeg")
    
    return (codeChar, codeHashName)

if __name__ == "__main__":
    generate_verification_code()



