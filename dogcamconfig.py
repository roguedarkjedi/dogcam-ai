import json

class DogCamConfig():
	
	def __init__(self):
		with open("./config.json","r") as cfg_file:
			ConfigData = json.load(cfg_file)
			
			self.__dict__ = ConfigData
			
			print("Config data has been loaded!")
			
