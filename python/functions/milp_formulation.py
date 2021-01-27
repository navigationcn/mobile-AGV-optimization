"""
    Solves the MILP based on the current progress of the robots
"""

from mip import Model, xsum, maximize, minimize, BINARY, CONTINUOUS, Constr, ConstrList
import matplotlib.pyplot as plt
import networkx as nx
import time
import numpy as np

import logging
logger = logging.getLogger(__name__)

# epsilon boundary => required to avoid a1 >= b1 AND b1 >= a1 to be true simultaneously
eps = 0.01 #1

def solve_MILP(robots, dependency_groups, ADG, ADG_reverse, H_control, H_prediction, m, pl_opt, run=True, uncertainty_bound=0.0, cost_func="cumulative"):
    """
        Formulate and solve an MILP which uses:
         - each robot's current location
         - inter-robot dependencies represented by ADG
        to determine if the ordering should be revised

        If the ordering needs to be revised, the ADG is updated accordingly

        Dependencies can only be switched if none of the robots have reached the
        nodes linking these dependencies
    """
    if not run:
        logger.info(" solve_MILP: NOT running optimization - original behavior")
        return None, 0
    else:
        logger.info(" solve_MILP: Formulating and solving MILP ...")

    current_positions = {} # list of node ID's where the robots are
    for robot in robots:
        current_positions[robot.robot_ID] = robot.current_node

    """ 1 - Determine which edges can be reversed based on robot's current position """
    logger.info(" 1 determining switchable_dependency_groups ...")
    switchable_dependency_groups = []   # list of dependency groups which CAN be switched
    fixed_dependency_groups = []        # list of dependency groups which CANNOT be switched

    for dependency_group in dependency_groups:
        logger.debug("dependency group type: {}".format(dependency_group.type))
        group_is_switchable = True
        blocked_robot_ID = dependency_group.robot_blocked
        blocking_robot_ID = dependency_group.robot_blocking

        # check the original dependency edges
        for edge in dependency_group.edges:
            node_pointing_to = edge[1]  # the node the edge is pointing to
            plan_idx = node_pointing_to.split("_")[2] # get the plan number "p_0_2" = 2
            current_robot_plan_idx = current_positions[int(blocked_robot_ID)].split("_")[2]
            if int(plan_idx) <= int(current_robot_plan_idx):
                group_is_switchable = False

        # check the reverse dependency edges
        for edge in dependency_group.reverse_edges:
            node_pointing_to = edge[1] # the node the edge is pointing to
            plan_idx = node_pointing_to.split("_")[2] # get the plan number "p_0_2" = 2
            current_robot_plan_idx = current_positions[int(blocking_robot_ID)].split("_")[2]
            if int(plan_idx) <= int(current_robot_plan_idx):
                group_is_switchable = False

        # check if closest head is within horizon
        tail = dependency_group.first_edge_tail
        head = dependency_group.first_edge_head
        head_robot_id = int(head.split("_")[1])
        head_pos_idx = int(head.split("_")[2])
        robot_node = current_positions[head_robot_id]
        robot_pos_idx = int(robot_node.split("_")[2])
        if head_pos_idx > robot_pos_idx + H_control: # if outside horizon
            group_is_switchable = False

        # if dependencies are switchable, add to list
        if group_is_switchable:
            switchable_dependency_groups.append(dependency_group)
        else:
            fixed_dependency_groups.append(dependency_group)

    # logger.debug("Length: {}".format(len(switchable_dependency_groups)))
    logger.info("   done!")

    """ 2 - Formulate MILP using switchable_dependency_groups """
    logger.info(" 2 formulating MILP problem ...")

    M = 1000000 # Big-M method - Niels: "choose wisely to help solver numerically"

    # m_opt.start = #TODO INITIAL FEASIBLE SOLUTION - Ch 5.4 of MIP manual
    milp_variables = {}
    milp_variables["continuous"] = {}
    milp_variables["binary"] = []

    # Define continuous variables and constraints
    logger.debug("    - adding continuous constraints ...")
    for robot in robots:
        milp_variables["continuous"][robot.robot_ID] = {}
        time_to_next_node = robot.get_remaining_times_to_next_node()
        for idx, node in enumerate(robot.get_remaining_plan()):
            milp_variables["continuous"][robot.robot_ID][node] = m.add_var(var_type="C")
            # add first node constraint
            if idx == 0:
                progress = 0.14 # change later in robot.object
                left_over = (1-progress)
                this_node = node
                this_node_var = milp_variables["continuous"][robot.robot_ID][node]
                m += this_node_var >= left_over*time_to_next_node[idx] + eps + uncertainty_bound
                prev_node_var = this_node_var
                prev_node = this_node
                logger.debug("      {} >= {}".format(node, left_over*time_to_next_node[idx]))
            else:
                this_node_var = milp_variables["continuous"][robot.robot_ID][node]
                m += this_node_var >= prev_node_var + time_to_next_node[idx] + eps + uncertainty_bound
                logger.debug("      {} >= {} + {}".format(node, prev_node, time_to_next_node[idx]))
                prev_node = node
                prev_node_var = this_node_var

    # Define binary (dependency) variables and constraints
    logger.debug("    - adding binary constraints ...")
    for dependency_group in switchable_dependency_groups:
        binary_variable = m.add_var(var_type="B")
        milp_variables["binary"].append(binary_variable)

        # define constraints
        for edge in dependency_group.edges:
            tail_node = edge[0]
            head_node = edge[1]

            tail_robot_id = int(tail_node.split("_")[1])
            head_robot_id = int(head_node.split("_")[1])

            tail_variable = milp_variables["continuous"][tail_robot_id][tail_node]
            head_variable = milp_variables["continuous"][head_robot_id][head_node]

            m += head_variable >= tail_variable + eps - binary_variable*M
            logger.debug("      {} >= {} - {}M".format(head_node, tail_node, binary_variable))

        for edge in dependency_group.reverse_edges:
            tail_node = edge[0]
            head_node = edge[1]

            tail_robot_id = int(tail_node.split("_")[1])
            head_robot_id = int(head_node.split("_")[1])

            tail_variable = milp_variables["continuous"][tail_robot_id][tail_node]
            head_variable = milp_variables["continuous"][head_robot_id][head_node]

            m += head_variable >= tail_variable + eps - (1.0 - binary_variable)*M
            logger.debug("      {} >= {} - (1-{})M".format(head_node, tail_node, binary_variable))

    logger.debug("    - adding fixed dependency constraints ...")
    for dependency_group in fixed_dependency_groups:
        if dependency_group.original_direction:
            for edge in dependency_group.edges:
                tail_node = edge[0]
                head_node = edge[1]

                tail_robot_id = int(tail_node.split("_")[1])
                head_robot_id = int(head_node.split("_")[1])
                try:
                    tail_variable = milp_variables["continuous"][tail_robot_id][tail_node]
                    head_variable = milp_variables["continuous"][head_robot_id][head_node]

                    m += head_variable >= tail_variable + eps
                    logger.debug("      {} >= {} ".format(head_node, tail_node))
                except KeyError:
                    pass
        else:
            for edge in dependency_group.reverse_edges:
                tail_node = edge[0]
                head_node = edge[1]

                tail_robot_id = int(tail_node.split("_")[1])
                head_robot_id = int(head_node.split("_")[1])
                try:
                    tail_variable = milp_variables["continuous"][tail_robot_id][tail_node]
                    head_variable = milp_variables["continuous"][head_robot_id][head_node]

                    m += head_variable >= tail_variable + eps
                    logger.debug("      {} >= {} ".format(head_node, tail_node))
                except KeyError:
                    pass

    logger.info(" 3 define cost function and solve MILP ...")
    logger.info("   - using solver: {}".format(m.solver_name))
    cont_var_count = sum([len(milp_variables["continuous"][robot_vars]) for robot_vars in milp_variables["continuous"]])
    binary_var_count = len(milp_variables["binary"])
    logger.info("   - cont.  variables: {}".format(cont_var_count))
    logger.info("   - binary variables: {}".format(binary_var_count))

    # define cost function
    # get the goal nodes
    goal_node_variables = []
    for robot in robots:
        robot_id = int(robot.robot_ID)
        node_name = robot.get_goal_node()
        goal_node = milp_variables["continuous"][robot_id][node_name]
        goal_node_variables.append(goal_node)

    # get all the continuous nodes
    node_variables = []
    for robot in robots:
        robot_id = int(robot.robot_ID)
        for node in milp_variables["continuous"][robot_id]:
            node_variables.append(node)


    # DIFFERENT OBJECTIVE FUNCTIONS
    #
    # 1) Makespan optimization min max(t_g(v_i^k)) for all v_i^k \in \mathcal{V}_{ADG}
    OBJECTIVE_FUNC = cost_func # cumulative, max, binary_penalty 
    if OBJECTIVE_FUNC == "max":
        z = m.add_var('z')
        m.objective = minimize(z)

        for goal_node in goal_node_variables:
            m += goal_node <= z

    if OBJECTIVE_FUNC == "cumulative":
        m.objective = minimize(xsum(goal_node_variables))

    if OBJECTIVE_FUNC == "bp_kb_10":
        # Add a cost for binary variables = 1! (To discourage switching if NOT ABSOLUTELY NECESSARY)
        if binary_var_count > 0:
            # c = np.array(binary_var_count*[100000.0])
            # logger.info("   - c: {}".format(c))
            # logger.info("   - bin var's: {}".format(milp_variables["binary"]))
            bin_vars = milp_variables["binary"]
            K_d = 10
            I = range(binary_var_count)
            m.objective = minimize(xsum(goal_node_variables) + xsum(bin_vars[i]*(K_d) for i in I))
        else:
            # If not binary variables:
            m.objective = minimize(xsum(goal_node_variables))
    
    if OBJECTIVE_FUNC == "bp_kb_2":
        # Add a cost for binary variables = 1! (To discourage switching if NOT ABSOLUTELY NECESSARY)
        if binary_var_count > 0:
            # c = np.array(binary_var_count*[100000.0])
            # logger.info("   - c: {}".format(c))
            # logger.info("   - bin var's: {}".format(milp_variables["binary"]))
            bin_vars = milp_variables["binary"]
            K_d = 2
            I = range(binary_var_count)
            m.objective = minimize(xsum(goal_node_variables) + xsum(bin_vars[i]*(K_d) for i in I))
        else:
            # If not binary variables:
            m.objective = minimize(xsum(goal_node_variables))
    
    if OBJECTIVE_FUNC == "bp_kb_5":
        # Add a cost for binary variables = 1! (To discourage switching if NOT ABSOLUTELY NECESSARY)
        if binary_var_count > 0:
            # c = np.array(binary_var_count*[100000.0])
            # logger.info("   - c: {}".format(c))
            # logger.info("   - bin var's: {}".format(milp_variables["binary"]))
            bin_vars = milp_variables["binary"]
            K_d = 5
            I = range(binary_var_count)
            m.objective = minimize(xsum(goal_node_variables) + xsum(bin_vars[i]*(K_d) for i in I))
        else:
            # If not binary variables:
            m.objective = minimize(xsum(goal_node_variables))
    
    if OBJECTIVE_FUNC == "bp_kb_1":
        # Add a cost for binary variables = 1! (To discourage switching if NOT ABSOLUTELY NECESSARY)
        if binary_var_count > 0:
            # c = np.array(binary_var_count*[100000.0])
            # logger.info("   - c: {}".format(c))
            # logger.info("   - bin var's: {}".format(milp_variables["binary"]))
            bin_vars = milp_variables["binary"]
            K_d = 1
            I = range(binary_var_count)
            m.objective = minimize(xsum(goal_node_variables) + xsum(bin_vars[i]*(K_d) for i in I))
        else:
            # If not binary variables:
            m.objective = minimize(xsum(goal_node_variables))

    if OBJECTIVE_FUNC == "greedy":
        m.objective = minimize(xsum(node_variables))
        


    # solve the MILP
    m.verbose = 0

    ### SOLVE THE MILP
    start = time.process_time()
    opt_success = True
    try:
        res = m.optimize(max_seconds=600) # max 10 minute solve time
        logger.info("   -> optimized cost: {}".format(m.objective_value));
        logger.info("   solver status: {}".format(res))
        solver_time = time.process_time() - start
        logger.info("   solver time: {} s".format(solver_time))
        logger.info(" 4 results of MILP solution:")
        logger.debug("    Result: {}".format(res))

        for binary_variable in milp_variables["binary"]:
            logger.debug("    {} : {}".format(binary_variable, binary_variable.x))
    except:
        # The optimization failed and returned an infeasible solution?
        opt_success = False
        return None, None

    logger.info(" 5 update the ADG based on new optimal solution")

    # remove all dependencies (all Type 2 edges)
    edges_all = ADG.edges(data=True)
    edges_type_2 = [edge for edge in edges_all if edge[2]["type"] == 2]

    logger.debug("    edges  (all)  : {}".format(edges_all))
    logger.debug("    edges (Type 2): {}".format(edges_type_2))

    logger.debug("    ADG Edges 0: {}".format(ADG.edges(data=True)))
    ADG.remove_edges_from(edges_type_2)
    logger.debug("    ADG Edges 1: {}".format(ADG.edges(data=True)))

    # add fixed dependency groups
    for dependency_group in fixed_dependency_groups:
        if dependency_group.original_direction:
            for edge in dependency_group.edges:
                ADG.add_edge(edge[0], edge[1], type=2)
        else:
            for edge in dependency_group.reverse_edges:
                ADG.add_edge(edge[0], edge[1], type=2)
        # ADG.add_edges_from(dependency_group.edges)

    # add active switchable_dependency_groups based on MILP results
    dependency_idx = 0
    binary_true_count = 0
    binary_false_count = 0
    for dependency_group in switchable_dependency_groups:
        if milp_variables["binary"][dependency_idx].x > 0.999999999999999:
            binary_true_count += 1
            dependency_group.original_direction = False
            for edge in dependency_group.reverse_edges:
                ADG.add_edge(edge[0], edge[1], type=2)
        elif milp_variables["binary"][dependency_idx].x < 0.00001:
            dependency_group.original_direction = True
            binary_false_count += 1
            for edge in dependency_group.edges:
                ADG.add_edge(edge[0], edge[1], type=2)
        else:
            logger.error("Binary variable is NOT binary!")
        dependency_idx += 1

    logger.debug("    ADG Edges 2: {}".format(ADG.edges(data=True)))

    ADG_reverse = ADG.reverse(copy=False)

    logger.info("   - set variables     : {} / {}".format(binary_true_count, binary_var_count))
    logger.info("   - cleared variables : {} / {}".format(binary_false_count, binary_var_count))
    logger.info(" done! ")

    # return result status of the optimizer
    return res, solver_time
