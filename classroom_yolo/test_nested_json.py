import json

conf_zonal = json.load(open('config_zones.json'))
zonal = conf_zonal["C201R"]["zonal"]
no_of_zones = conf_zonal["C201R"]["no_of_zones"]
#print zonal,no_of_zones

conf = json.load(open('config_main.json'))

data_id = conf["201"]["data_id"]
port_no = conf["201"]["port_no"]
cam_urls = conf["201"]["camera_urls"]
#print data_id, port_no, cam_urls

conf_image = json.load(open('config_imageprocessing.json'))
thresh = conf_image["Threshold Area"]
#print thresh


