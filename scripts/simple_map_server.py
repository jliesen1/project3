#!/usr/bin/env python

import rospy, yaml
from nav_msgs.msg import OccupancyGrid, MapMetaData
from nav_msgs.srv import GetMap, GetMapResponse

def load_pgm(path):
    with open(path, 'rb') as f:
        raw = f.read()

    parts = raw.split(None, 4)

    magic = parts[0]
    w = int(parts[1])
    h = int(parts[2])
    maxval = int(parts[3])

    if magic == 'P5':
        pixels = [ord(c) for c in parts[4][:w*h]]
    elif magic == 'P2':
        pixels = [int(x) for x in parts[4].split()]
    else:
        raise Exception("Unsupported PGM type: " + magic)

    occ = []
    for v in pixels:
        if v < 65:
            occ.append(100)
        elif v > 250:
            occ.append(0)
        else:
            occ.append(-1)

    return w, h, occ

def handle_get_map(req):
    return GetMapResponse(grid)

rospy.init_node('simple_map_server')

yaml_file = rospy.get_param('~map_file')
with open(yaml_file, 'r') as f:
    info = yaml.safe_load(f)

image_path = yaml_file.rsplit('/', 1)[0] + '/' + info['image']
w, h, data = load_pgm(image_path)

grid = OccupancyGrid()
grid.header.frame_id = 'map'
grid.info.resolution = float(info['resolution'])
grid.info.width = w
grid.info.height = h
grid.info.origin.position.x = float(info['origin'][0])
grid.info.origin.position.y = float(info['origin'][1])
grid.info.origin.orientation.w = 1.0
grid.data = data

pub = rospy.Publisher('/map', OccupancyGrid, queue_size=1, latch=True)
meta_pub = rospy.Publisher('/map_metadata', MapMetaData, queue_size=1, latch=True)
srv = rospy.Service('/static_map', GetMap, handle_get_map)

rate = rospy.Rate(1)
while not rospy.is_shutdown():
    grid.header.stamp = rospy.Time.now()
    pub.publish(grid)
    meta_pub.publish(grid.info)
    rate.sleep()
