import base64

def process_audio():
    encode_string = base64.b64encode(open("itsmebenjamin.wav", "rb").read())
    wav_file = open("temp.wav", "wb")
    decode_string = base64.b64decode(encode_string)
    wav_file.write(decode_string)
    return None
