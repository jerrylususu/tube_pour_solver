from typing import List, Union, Tuple, Set
from collections import Counter
import json
from queue import PriorityQueue
from itertools import combinations, chain, combinations_with_replacement

class Tube:
    def __init__(self, content_or_tube):
        # first: lowest, last: highest
        if isinstance(content_or_tube, Tube):
            self.content = content_or_tube.content[:]
        elif isinstance(content_or_tube, list):
            self.content : List = content_or_tube

    @property
    def last_color_count(self):
        if self.empty:
            return 0
        last_color = self.content[-1]
        count = 1
        for i in range(len(self.content) - 2, -1, -1):
            if self.content[i] == last_color:
                count += 1
            else:
                break
        return count


    def pour_out(self):
        last_color = self.content[-1]
        poured_out = []
        while len(self.content) > 0 and self.content[-1] == last_color:
            poured_out.append(self.content.pop())
        return poured_out

    def pour_in(self, colors):
        if len(self.content) == 0:
            pass
        elif self.content[-1] != colors[0]:
            raise Exception("incompatible colors")

        self.content = self.content + colors


    @property
    def mix_value(self):
        color_count = len(set(self.content))
        # return color_count
        if color_count == 0:
            return 0
        elif color_count == 1:
            return 1
        else:
            return color_count + 1

    @property
    def empty(self):
        return len(self.content) == 0
    
    @property
    def top(self):
        return self.content[-1]

    def __eq__(self, other):
        return self.content == other.content

    def __hash__(self) -> int:
        return hash(str(self.content))

    def __str__(self):
        return self.content.__str__()

    def __repr__(self):
        return repr(self.content)

class State:
    # basically a multiset
    def __init__(self, tubes_or_state, cost=0):
        self.internal_dict = {}
        self.cost = cost
        if type(tubes_or_state) is State:
            self.internal_dict = dict(tubes_or_state.internal_dict)
        elif type(tubes_or_state) is list:
            self.internal_dict = dict(Counter(tubes_or_state))

    
    def perform_move(self, tube_src, tube_dst):
        if tube_src not in self.internal_dict or self.internal_dict[tube_src] == 0:
            raise Exception("tube_src not in state")
        if tube_dst not in self.internal_dict or self.internal_dict[tube_dst] == 0:
            raise Exception("tube_dst not in state")
            
        self.internal_dict[tube_src] -= 1
        self.internal_dict[tube_dst] -= 1

        if tube_src in self.internal_dict and self.internal_dict[tube_src] == 0:
            self.internal_dict.pop(tube_src)
        if tube_dst in self.internal_dict and self.internal_dict[tube_dst] == 0:
            self.internal_dict.pop(tube_dst)

        src = Tube(tube_src)
        dst = Tube(tube_dst)

        dst.pour_in(src.pour_out())

        self.internal_dict[src] = self.internal_dict.get(src, 0) + 1
        self.internal_dict[dst] = self.internal_dict.get(dst, 0) + 1        

    @property
    def mix_value(self):
        sum_value = 0
        for tube, count in self.internal_dict.items():
            sum_value += tube.mix_value * count
        return sum_value
    
    @property
    def target_mix_value(self):
        color_set = set()
        for tube in self.internal_dict.keys():
            color_set.update(tube.content)
        return len(color_set)

    def __hash__(self) -> int:
        str_key_dict = {repr(k):v for k,v in self.internal_dict.items()}
        return hash(json.dumps(str_key_dict, sort_keys=True))

    def __str__(self):
        return f"{str(self.internal_dict)}"
    
    def __repr__(self):
        return self.internal_dict.__repr__()

    def __eq__(self, other):
        return self.internal_dict == other.internal_dict

    def __lt__(self, other):
        if self.mix_value + self.cost != other.mix_value + other.cost: 
            return self.mix_value + self.cost < other.mix_value + other.cost
        else:
            return str(self) < str(other)

def generate_moves(state: State):
    new_state_with_move = []

    tubes_having_2_or_more = [(tube, tube) for tube in state.internal_dict.keys() if state.internal_dict[tube] >= 2]

    for tube1, tube2 in chain(tubes_having_2_or_more, combinations(state.internal_dict.keys(), 2)):

        moves = [(tube1, tube2)]
        if tube1 != tube2:
            moves.append((tube2, tube1))

        for tube_src, tube_dst in moves:

            move = (str(tube_src), str(tube_dst))
            # print(move)
            # skip condition
            if tube_src.empty:
                # empty source
                continue
            if not tube_dst.empty and tube_src.top != tube_dst.top:
                # incompatible colors
                continue
            if tube_src.mix_value == 1 and tube_dst.empty:
                # useless move
                continue
            if len(tube_dst.content) >= 4:
                # overflow
                continue
            if tube_src.last_color_count + len(tube_dst.content) > 4:
                # overflow
                continue

            # print(move , " accepted")

            new_state = State(state, cost=state.cost + 1)
            new_state.perform_move(tube_src, tube_dst)
            new_state_with_move.append((new_state, move))
            # print("new state", new_state)
            # input()

    return new_state_with_move


def a_star_search(initial_state: State):
    target = initial_state.target_mix_value

    frontier = PriorityQueue() # lowest priority first
    # item: (state, moves), priority: mix_value
    frontier.put((initial_state, list()))

    existing_states = set()
    existing_states.add(initial_state)

    while not frontier.empty():

        (state, moves) = frontier.get()
        # print(state)
        # input()

        # print(f"{len(frontier.queue)} states remaining", state.mix_value, state.cost)

        if state.mix_value == target:
            # print("found!")
            # print(state)
            return moves
        
        for new_state, move in generate_moves(state):
            if new_state in existing_states:
                continue
            new_move = moves.copy()
            new_move.append(move)
            frontier.put((new_state, new_move))
            existing_states.add(new_state)

def main():

#  example 1

#    tubes = [
#        Tube([4,3,2,1]),
#        Tube([7,5,6,5]),
#        Tube([3,9,7,8]),
#        Tube([9,1,2,10]),
#        Tube([7,4,1,9]),
#        Tube([6,8,12,11]),
#        Tube([12,12,4,10]),
#        Tube([7,10,2,1]),
#        Tube([2,5,5,10]),
#        Tube([8,4,3,9]),
#        Tube([6,12,11,3]),
#        Tube([8,11,11,6]),
#        Tube([]),
#        Tube([])
#    ]

#  example 2

    tubes = [
        Tube([3,3,2,1]),
        Tube([6,5,2,4]),
        Tube([8,1,7,1]),
        Tube([11,9,10,9]),
        Tube([6,1,6,10]),
        Tube([2,12,11,12]),
        Tube([8,9,2,5]),
        Tube([11,10,7,4]),
        Tube([4,10,12,8]),
        Tube([3,11,6,7]),
        Tube([5,7,5,8]),
        Tube([4,12,9,3]),
        Tube([]),
        Tube([]),
    ]

    # print(tubes)
    state = State(tubes)
    # print(state)

    # print(state.target_mix_value)

    found_moves = a_star_search(state)
    print("required moves:", len(found_moves))

    for idx, move in enumerate(found_moves):
        print(f"{idx+1}: {move[0]} -> {move[1]}")



if __name__ == "__main__":
    main()