import logging
logger = logging.getLogger(__name__)

class Robot(object):
    def __init__(self, robot_ID, robot_plan, color, goal_position):
        self.robot_ID = robot_ID
        self.plan_nodes = robot_plan["nodes"]
        self.plan_positions = robot_plan["positions"]
        self.goal_position = goal_position
        self.plan_length = len(self.plan_nodes)
        self.color = [color]
        self.advance_this_step = False
        # at the moment, distance to goal is always 1.0, BUT can change later!
        self.time_to_next_node = [1.0]*(self.plan_length)
        # a vector which is the estimated time taken for the robot to reach the next node
        self.current_idx = 0
        self.delay_val = 0
        self.current_node = self.plan_nodes[self.current_idx]
        self.current_position = self.plan_positions[self.current_idx]
        self.prev_position = self.current_position
        self.goal_reached_animate = False # animation boolean only
        if self.current_idx == self.plan_length:
            self.status = "done"
            self.current_position = {"x" : self.goal_position["x"], "y" : self.goal_position["y"]}
        else:
            self.status = "not done"

    def get_position(self):
        return self.current_position

    def get_prev_position(self):
        return self.prev_position

    def get_color(self):
        return self.color

    def get_delay(self):
        return self.delay_val

    def increase_delay(self, delay):
        self.delay_val += delay

    def delay_inc_timestep(self):
        if self.delay_val > 0:
            self.delay_val -= 1

    def advance(self):
        if self.current_idx < self.plan_length - 1:
            self.advance_this_step = True
            self.current_idx += 1
            self.current_node = self.plan_nodes[self.current_idx]
            self.current_position = self.plan_positions[self.current_idx]
            self.prev_position = self.plan_positions[max(self.current_idx-1,0)]
            # logger.info("self.current_node: {}".format(self.current_node))
        else:
            if not self.goal_reached_animate: # check if animation to goal has been shown
                self.advance_this_step = True
                self.prev_position = self.current_position
                self.current_position = {"x" : self.goal_position["x"], "y" : self.goal_position["y"]}
                self.goal_reached_animate = True
            else: # if the animation of the robot to the goal has already been shown
                logger.debug("Robot {}: end of plan reached, staying in place".format(self.robot_ID))
                self.advance_this_step = False
                self.status = "done"
                self.current_position = {"x" : self.goal_position["x"], "y" : self.goal_position["y"]}
                self.prev_position = self.current_position

    def get_remaining_plan(self):
        return self.plan_nodes[self.current_idx:]

    def get_remaining_times_to_next_node(self):
        return self.time_to_next_node[self.current_idx:]

    def get_goal_node(self):
        return self.plan_nodes[-1]

    def is_done(self):
        return self.status == "done"
