"""
	Object which represents the data required to define a node in an Action
	Depenency Graph (ADG)
"""

from enum import Enum
class Status(Enum):
	STAGED = 1
	ENQUEUED = 2
	FINISHED = 3

class ADGNode(object):
	def __init__(self, ID, item, next_item):
		self.ID = ID # p_k_i
		time = item["t"]
		sx = item["x"]
		sy = item["y"]
		gx = next_item["x"]
		gy = next_item["y"]
		self.time = time
		self.s_loc = (sx, sy)
		self.g_loc = (gx, gy)
		self.status = Status.STAGED
		self.info = str(ID) + "\n s("+str(sx)+","+str(sy)+")"+" \n g("+str(gx)+","+str(gy)+")" + "\n t " + str(time)
