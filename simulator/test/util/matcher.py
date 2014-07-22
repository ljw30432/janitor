'''
Created on 20 Jun 2014

@author: jack
'''

class ModelMatcher:

    def __init__(self, test_case):
        self.test_case = test_case

    def with_model(self, model):
        self.model = model
        return self

    def with_agent(self, agent):
        self.agent_name = agent
        return self

    def at(self, at):
        actual = self.model["agents"][self.agent_name]["at"][1]
        self.test_case.assertEqual(actual, at)

    def with_distance(self, distance):
        self.distance = distance
        return self

    def from_(self, from_node):
        self.from_node = from_node
        return self

    def to(self, to_node):
        self.to_node = to_node
        edge = [self.from_node, self.to_node, self.distance]
        self.test_case.assertIn(edge, self.model["graph"]["edges"])

    def with_node(self, node, not_room=None, **kwargs):
        self.node = node
        self.node_value = kwargs
        if not not_room:
            if "known" in kwargs:
                kwargs["known"]["is-room"] = True
            else:
                kwargs["is-room"] = True
        self.test_case.assertIn(node, self.model["nodes"])
        self.test_case.assertEqual(self.model["nodes"][node], kwargs)



    def __call__(self, model):
        return ModelMatcher(self.test_case).with_model(model)