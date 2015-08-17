from _collections_abc import Sequence
from itertools import chain
from numbers import Number
from pddl_parser import get_text_file_handle

__author__ = 'jack'


def encode_problem_to_file(filename, model, agent, goals, tils):
    with get_text_file_handle(filename) as fh:
        encode_problem(fh, model, agent, goals, tils)


def encode_problem(out, model, agent, goals, tils):

    has_metric = "metric" in model

    _encode_preamble(out, "problem-name", model["domain"], has_metric)

    agent_names = model["agents"].keys() if agent == "all" else (agent,)
    _encode_objects(out, chain(agent_names, model["nodes"].keys()))

    agent_values = model["agents"] if agent == "all" else {agent: model["agents"][agent]}
    _encode_init(out, agent_values, model["nodes"], model["graph"], model["assumed-values"], tils)

    _encode_goal(out, goals if goals else model["goal"])

    if has_metric:
        _encode_metric(out, model["metric"])

    # post-amble
    out.write(")")


def _encode_preamble(out, problem_name, domain_name, requires_preferences):
    out.write("(define (problem ")
    out.write(problem_name)
    out.write(") (:domain ")
    out.write(domain_name)
    out.write(")")
    if requires_preferences:
        out.write(" (:requirements :preferences)")
    out.write("\n")


def _encode_objects(out, objects):
    out.write("(:objects ")
    for obj in objects:
        out.write(" ")
        out.write(obj)
    out.write(")\n")


def _encode_init(out, agents, nodes, graph, assumed_values, tils=None):
    out.write("(:init ")
    _encode_init_helper(out, agents, assumed_values)
    _encode_init_helper(out, nodes, assumed_values)
    if tils:
        for til in tils:
            _encode_predicate(out, til.as_predicate())
    _encode_graph(out, graph)
    out.write(") ")


def _encode_init_helper(out, items, assumed_values):
    for object_name, object_values in items.items():
        if "known" not in object_values:
            _encode_init_values(out, object_name, object_values)
        else:
            _encode_init_values(out, object_name, object_values["known"])
            _encode_init_values(out, object_name, object_values["unknown"], assumed_values, unknown_value_getter)


def _encode_init_values(out, object_name, object_values, assumed_values=None, value_getter=(lambda x, _0, _1: x)):
    for value_name, possible_values in object_values.items():
        value = value_getter(possible_values, value_name, assumed_values)
        if value is False:
            pass
        elif value is True:
            _encode_predicate(out, (value_name, object_name))
        elif isinstance(value, Number):
            _encode_function(out, (value_name, object_name), value)
        elif isinstance(value, Sequence):
            if isinstance(value[-1], Number):
                pred_values = (value_name,) + tuple(x if not isinstance(x, bool) else object_name for x in value[:-1])
                _encode_function(out, pred_values, value[-1])
            else:
                pred_values = (value_name,) + tuple(x if not isinstance(x, bool) else object_name for x in value)
                _encode_predicate(out, pred_values)


def unknown_value_getter(possible_values, object_name, assumed_values):
    if "assumed" in possible_values:
        return possible_values["assumed"]
    value = assumed_values[object_name]
    if value in possible_values:
        return possible_values[value]
    else:
        return value


def _encode_predicate(out, args):
    out.write("(")
    for arg in args:
        if isinstance(arg, (list, tuple)):
            _encode_predicate(out, arg)
        else:
            out.write(str(arg))
        out.write(" ")
    out.write(") ")


def _encode_function(out, args, value):
    out.write("(= ")
    _encode_predicate(out, args)
    out.write(str(value))
    out.write(") ")


def _encode_graph(out, graph):

    for node0, node1, value in graph["edges"]:
        _encode_predicate(out, ("edge", node0, node1))
        _encode_function(out, ("distance", node0, node1), value)

    if graph["bidirectional"]:
        for node0, node1, value in graph["edges"]:
            _encode_predicate(out, ("edge", node1, node0))
            _encode_function(out, ("distance", node1, node0), value)


def _encode_goal(out, goals):
    out.write("(:goal (and ")
    if isinstance(goals, list):
        for goal in goals:
            _encode_predicate(out, goal)
    else:  # is dict
        for goal in goals["hard-goals"]:
            _encode_predicate(out, goal)
        if "preferences" in goals:
            for preference in goals["preferences"]:
                _encode_predicate(out, ["preference"] + preference)
    out.write("))\n")


def _encode_metric(out, metric):
    out.write("(:metric ")
    out.write(metric["type"])
    out.write(" ")
    _encode_predicate(out, metric["predicate"])
    out.write(")\n")