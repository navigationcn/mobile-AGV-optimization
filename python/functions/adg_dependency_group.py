"""
    Object which defines a group of dependencies between two robots.
    Dependencies can be either:
     0 single - only a single dependency (one edge in the ADG)
     1 same - a group of edges where robots move in the same direction
     2 opposite - a group of edges where robots move in opposite direction
"""

import logging
logger = logging.getLogger(__name__)

from enum import Enum
class GroupType(Enum):
    single = 0
    same = 1
    opposite = 2

class DependencyGroup(object):
    def __init__(self, edge):
        self.edges = []
        self.edges.append(edge)
        self.reverse_edges = []
        self.type = GroupType.single # 0 single, 1 same, 2 opposite
        self.robot_blocking = edge[0].split("_")[1]
        self.robot_blocked = edge[1].split("_")[1]
        self.original_direction = True # false if reverse_edges are active
        self.first_edge_tail = edge[0]
        self.first_edge_head = edge[1]

    def __add_edge(self, edge):
        self.edges.append(edge)

    def next_edge_same(self, edge):
        if self.type == GroupType.single or self.type == GroupType.same:
            current_edge = self.edges[-1]
            u_curr = current_edge[0]
            v_curr = current_edge[1]
            spl_u = u_curr.split("_")
            spl_v = v_curr.split("_")
            u_next = spl_u[0] + "_" + spl_u[1] + "_" + str(int(spl_u[2])+1)
            v_next = spl_v[0] + "_" + spl_v[1] + "_" + str(int(spl_v[2])+1)
            logger.debug("edge[0] {} == u_next {} and edge[1] {} == v_next {}".format(edge[0], u_next, edge[1], v_next))
            if edge[0] == u_next and edge[1] == v_next:
                logger.debug("changed to same")
                self.type = GroupType.same
                self.__add_edge(edge)
                return True
            else:
                return False
        else:
            return False

    def next_edge_opposite(self, edge):
        if self.type == GroupType.single or self.type == GroupType.opposite:
            current_edge = self.edges[-1]
            u_curr = current_edge[0]
            v_curr = current_edge[1]
            spl_u = u_curr.split("_")
            spl_v = v_curr.split("_")
            u_next = spl_u[0] + "_" + spl_u[1] + "_" + str(int(spl_u[2])+1)
            v_next = spl_v[0] + "_" + spl_v[1] + "_" + str(int(spl_v[2])-1)
            logger.debug("edge[0] {} == u_next {} and edge[1] {} == v_next {}".format(edge[0], u_next, edge[1], v_next))
            if edge[0] == u_next and edge[1] == v_next:
                logger.debug("changed to opposite")
                self.type = GroupType.opposite
                self.__add_edge(edge)
                self.first_edge_head = edge[1]
                return True
        else:
            return False

    def determine_reverse(self):
        if self.type == GroupType.single:
            # single arrow -> self.edges has length 1
            edge = self.edges[0]
            u_curr = edge[0]
            v_curr = edge[1]
            spl_u = u_curr.split("_")
            spl_v = v_curr.split("_")
            v_new = spl_u[0] + "_" + spl_u[1] + "_" + str(int(spl_u[2])-1) # was +1
            u_new = spl_v[0] + "_" + spl_v[1] + "_" + str(int(spl_v[2])+1) # was -1
            self.reverse_edges.append((u_new, v_new))
            # v_new = spl_u[0] + "_" + spl_u[1] + "_" + str(int(spl_u[2])+1) # was +1
            # u_new = spl_v[0] + "_" + spl_v[1] + "_" + str(int(spl_v[2])-1) # was -1
            # self.reverse_edges.append((u_new, v_new))
            # v_new = spl_u[0] + "_" + spl_u[1] + "_" + str(int(spl_u[2])) # was +1
            # u_new = spl_v[0] + "_" + spl_v[1] + "_" + str(int(spl_v[2])) # was -1
            # self.reverse_edges.append((u_new, v_new))
        elif self.type == GroupType.same:
            for edge in self.edges:
                u_curr = edge[0]
                v_curr = edge[1]
                spl_u = u_curr.split("_")
                spl_v = v_curr.split("_")
                v_new = spl_u[0] + "_" + spl_u[1] + "_" + str(int(spl_u[2])-1)
                u_new = spl_v[0] + "_" + spl_v[1] + "_" + str(int(spl_v[2])+1)
                self.reverse_edges.append((u_new, v_new))
        elif self.type == GroupType.opposite:
            for edge in self.edges:
                u_curr = edge[0]
                v_curr = edge[1]
                spl_u = u_curr.split("_")
                spl_v = v_curr.split("_")
                v_new = spl_u[0] + "_" + spl_u[1] + "_" + str(int(spl_u[2])-1)
                u_new = spl_v[0] + "_" + spl_v[1] + "_" + str(int(spl_v[2])+1)
                # u_new = v_curr
                # v_new = u_curr
                self.reverse_edges.append((u_new, v_new))
                # add last pointing edge










            #.
