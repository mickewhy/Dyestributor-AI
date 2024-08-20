import copy
import time


class Color:
    # https://gist.github.com/fnky/458719343aabd01cfb17a3a4f7296797
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    GRAY = "\033[90m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


class Node:
    def __init__(self, state, parent, action):
        self.state = state
        self.parent = parent
        self.action = action


class StackFrontier:
    def __init__(self):
        self.frontier = []

    def add(self, node):
        self.frontier.append(node)

    def contains_state(self, state):
        return any(node.state == state for node in self.frontier)

    def empty(self):
        return len(self.frontier) == 0

    def remove(self):
        if self.empty():
            raise Exception(Color.RED + "Empty frontier" + Color.ENDC)
        else:
            node = self.frontier[-1]
            self.frontier = self.frontier[:-1]
            return node


class QueueFrontier(StackFrontier):
    def remove(self):
        if self.empty():
            raise Exception(Color.RED + "Empty frontier" + Color.ENDC)
        else:
            node = self.frontier[0]
            self.frontier = self.frontier[1:]
            return node


class Puzzle:
    def __init__(self, start):

        # Test grid
        # self.start = [
        #     ["⬛", "⬛", "⬛", "⬛", "⬛"],
        #     ["⬛", "🖌️➡️", " ", "🎨⬅️", "⬛"],
        #     ["⬛", "⬛", "⬛", "⬛", "⬛"],
        # ]
        # Nugget grid
        # self.start = [
        #     ["⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛"],
        #     ["⬛", "⬛", "⬛", "🖌️⬆️", "⬛", "⬛", "⬛", "⬛"],
        #     ["⬛", "⬛", "⬛", "🟦", " ", "⬛", "⬛", "⬛"],
        #     ["⬛", "⬛", "⬛", "⬛", "❗", "⬛", "⬛", "⬛"],
        #     ["⬛", "⬛", " ", "❗", " ", " ", "⬛", "⬛"],
        #     ["⬛", "❗", "🟦", "⬛", "⬛", "🎨⬇️", "🟦", "⬛"],
        #     ["⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛", "⬛"],
        # ]
        # Ocean 1
        # self.start = [
        #     ["⬛", "⬛", "⬛", "⬛", "⬛", "⬛"],
        #     ["⬛", "⬛", " ", "❗", "⬛", "⬛"],
        #     ["⬛", " ", "⬛", "🖌️➡️", "🟦", "⬛"],
        #     ["⬛", "❗", "🎨⬅️", "🟦", "🟦", "⬛"],
        #     ["⬛", "⬛", " ", "❗", "⬛", "⬛"],
        #     ["⬛", "⬛", "⬛", "⬛", "⬛", "⬛"],
        # ]
        # Ocean 2
        # self.start = [
        #     ["⬛", "⬛", "⬛", "⬛", "⬛", "⬛"],
        #     ["⬛", " ", "🟦", "❗", "🖌️⬇️", "⬛"],
        #     ["⬛", " ", "❗", " ", "🟦", "⬛"],
        #     ["⬛", "❗", "⬛", "⬛", "⬛", "⬛"],
        #     ["⬛", " ", " ", " ", "🎨⬆️", "⬛"],
        #     ["⬛", "⬛", "⬛", "⬛", "⬛", "⬛"],
        # ]
        # Ocean 3
        # self.start = [
        #     ["⬛", "⬛", "⬛", "⬛", "⬛", "⬛"],
        #     ["⬛", "❗", "🟦", "❗", " ", "⬛"],
        #     ["⬛", " ", " ", "⬛", "🎨⬇️", "⬛"],
        #     ["⬛", "🖌️⬆️", "❗", "⬛", "❗", "⬛"],
        #     ["⬛", " ", " ", "❗", "🟦", "⬛"],
        #     ["⬛", "⬛", "⬛", "⬛", "⬛", "⬛"],
        # ]

        # Determine start
        self.start = start

        # Determine height and width of puzzle
        self.height = len(self.start)
        self.width = len(self.start[0])

        self.solution = None

    def neighbors(self, state):
        # ⬛ = IMMOVABLE BLOCK / WALL
        # 🟦 = MOVABLE BLOCK
        # ❗ = BOOM BLOCK
        # 🔄 = HORIZONTAL DIRECTIONAL BLOCK
        # 🔃 = VERTICAL DIRECTIONAL BLOCK
        # ⚡ = LIGHT BLOCK
        # 🖌️⬆️ = NORTH DYE INJECTOR BLOCK
        # 🖌️⬇️ = SOUTH DYE INJECTOR BLOCK
        # 🖌️⬅️ = WEST DYE INJECTOR BLOCK
        # 🖌️➡️ = EAST DYE INJECTOR BLOCK
        # 🎨⬆️ = NORTH DYE RECEIVER BLOCK
        # 🎨⬇️ = SOUTH DYE RECEIVER BLOCK
        # 🎨⬅️ = WEST DYE RECEIVER BLOCK
        # 🎨➡️ = EAST DYE RECEIVER BLOCK
        # ⬆️ = TOP DOUBLE MOVABLE BLOCK
        # ⬇️ = BOTTOM DOUBLE MOVABLE BLOCK
        # ⬅️ = LEFT DOUBLE MOVABLE BLOCK
        # ➡️ = RIGHT DOUBLE MOVABLE BLOCK
        # ❗⬆️ = TOP DOUBLE BOOM BLOCK
        # ❗⬇️ = BOTTOM DOUBLE BOOM BLOCK
        # ❗⬅️ = LEFT DOUBLE BOOM BLOCK
        # ❗➡️ = RIGHT DOUBLE BOOM BLOCK
        #   = EMPTY

        result = []
        for i in range(self.height):
            for j in range(self.width):
                match state[i][j]:
                    case "🟦":
                        if state[i - 1][j] == " ":
                            newState = copy.deepcopy(state)
                            newState[i - 1][j] = "🟦"
                            newState[i][j] = " "
                            result.append((f"({i},{j}) up", newState))
                        if state[i + 1][j] == " ":
                            newState = copy.deepcopy(state)
                            newState[i + 1][j] = "🟦"
                            newState[i][j] = " "
                            result.append((f"({i},{j}) down", newState))
                        if state[i][j - 1] == " ":
                            newState = copy.deepcopy(state)
                            newState[i][j - 1] = "🟦"
                            newState[i][j] = " "
                            result.append((f"({i},{j}) left", newState))
                        if state[i][j + 1] == " ":
                            newState = copy.deepcopy(state)
                            newState[i][j + 1] = "🟦"
                            newState[i][j] = " "
                            result.append((f"({i},{j}) right", newState))
                    case "❗":
                        if state[i - 1][j] == " ":
                            if not (
                                "❗" in state[i - 2][j]
                                or "❗" in state[i - 1][j - 1]
                                or "❗" in state[i - 1][j + 1]
                            ):
                                newState = copy.deepcopy(state)
                                newState[i - 1][j] = "❗"
                                newState[i][j] = " "
                                result.append((f"({i},{j}) up", newState))
                        if state[i + 1][j] == " ":
                            if not (
                                "❗" in state[i + 2][j]
                                or "❗" in state[i + 1][j - 1]
                                or "❗" in state[i + 1][j + 1]
                            ):
                                newState = copy.deepcopy(state)
                                newState[i + 1][j] = "❗"
                                newState[i][j] = " "
                                result.append((f"({i},{j}) down", newState))
                        if state[i][j - 1] == " ":
                            if not (
                                "❗" in state[i][j - 2]
                                or "❗" in state[i - 1][j - 1]
                                or "❗" in state[i + 1][j - 1]
                            ):
                                newState = copy.deepcopy(state)
                                newState[i][j - 1] = "❗"
                                newState[i][j] = " "
                                result.append((f"({i},{j}) left", newState))
                        if state[i][j + 1] == " ":
                            if not (
                                "❗" in state[i][j + 2]
                                or "❗" in state[i - 1][j + 1]
                                or "❗" in state[i + 1][j + 1]
                            ):
                                newState = copy.deepcopy(state)
                                newState[i][j + 1] = "❗"
                                newState[i][j] = " "
                                result.append((f"({i},{j}) right", newState))
                    case "🔄":
                        if state[i][j - 1] == " ":
                            newState = copy.deepcopy(state)
                            newState[i][j - 1] = "🔄"
                            newState[i][j] = " "
                            result.append((f"({i},{j}) left", newState))
                        if state[i][j + 1] == " ":
                            newState = copy.deepcopy(state)
                            newState[i][j + 1] = "🔄"
                            newState[i][j] = " "
                            result.append((f"({i},{j}) right", newState))
                    case "🔃":
                        if state[i - 1][j] == " ":
                            newState = copy.deepcopy(state)
                            newState[i - 1][j] = "🔃"
                            newState[i][j] = " "
                            result.append((f"({i},{j}) up", newState))
                        if state[i + 1][j] == " ":
                            newState = copy.deepcopy(state)
                            newState[i + 1][j] = "🔃"
                            newState[i][j] = " "
                            result.append((f"({i},{j}) down", newState))
                    case "⚡":
                        if state[i - 1][j] == " ":
                            newState = copy.deepcopy(state)
                            newState[i - 1][j] = "⚡"
                            newState[i][j] = " "
                            result.append((f"({i},{j}) up", newState))
                        if state[i + 1][j] == " ":
                            newState = copy.deepcopy(state)
                            newState[i + 1][j] = "⚡"
                            newState[i][j] = " "
                            result.append((f"({i},{j}) down", newState))
                        if state[i][j - 1] == " ":
                            newState = copy.deepcopy(state)
                            newState[i][j - 1] = "⚡"
                            newState[i][j] = " "
                            result.append((f"({i},{j}) left", newState))
                        if state[i][j + 1] == " ":
                            newState = copy.deepcopy(state)
                            newState[i][j + 1] = "⚡"
                            newState[i][j] = " "
                            result.append((f"({i},{j}) right", newState))
                    case "🖌️⬆️":
                        if state[i - 1][j] == " ":
                            newState = copy.deepcopy(state)
                            newState[i - 1][j] = "🖌️⬆️"
                            newState[i][j] = " "
                            result.append((f"({i},{j}) up", newState))
                        if state[i + 1][j] == " ":
                            newState = copy.deepcopy(state)
                            newState[i + 1][j] = "🖌️⬆️"
                            newState[i][j] = " "
                            result.append((f"({i},{j}) down", newState))
                        if state[i][j - 1] == " ":
                            newState = copy.deepcopy(state)
                            newState[i][j - 1] = "🖌️⬆️"
                            newState[i][j] = " "
                            result.append((f"({i},{j}) left", newState))
                        if state[i][j + 1] == " ":
                            newState = copy.deepcopy(state)
                            newState[i][j + 1] = "🖌️⬆️"
                            newState[i][j] = " "
                            result.append((f"({i},{j}) right", newState))
                    case "🖌️⬇️":
                        if state[i - 1][j] == " ":
                            newState = copy.deepcopy(state)
                            newState[i - 1][j] = "🖌️⬇️"
                            newState[i][j] = " "
                            result.append((f"({i},{j}) up", newState))
                        if state[i + 1][j] == " ":
                            newState = copy.deepcopy(state)
                            newState[i + 1][j] = "🖌️⬇️"
                            newState[i][j] = " "
                            result.append((f"({i},{j}) down", newState))
                        if state[i][j - 1] == " ":
                            newState = copy.deepcopy(state)
                            newState[i][j - 1] = "🖌️⬇️"
                            newState[i][j] = " "
                            result.append((f"({i},{j}) left", newState))
                        if state[i][j + 1] == " ":
                            newState = copy.deepcopy(state)
                            newState[i][j + 1] = "🖌️⬇️"
                            newState[i][j] = " "
                            result.append((f"({i},{j}) right", newState))
                    case "🖌️⬅️":
                        if state[i - 1][j] == " ":
                            newState = copy.deepcopy(state)
                            newState[i - 1][j] = "🖌️⬅️"
                            newState[i][j] = " "
                            result.append((f"({i},{j}) up", newState))
                        if state[i + 1][j] == " ":
                            newState = copy.deepcopy(state)
                            newState[i + 1][j] = "🖌️⬅️"
                            newState[i][j] = " "
                            result.append((f"({i},{j}) down", newState))
                        if state[i][j - 1] == " ":
                            newState = copy.deepcopy(state)
                            newState[i][j - 1] = "🖌️⬅️"
                            newState[i][j] = " "
                            result.append((f"({i},{j}) left", newState))
                        if state[i][j + 1] == " ":
                            newState = copy.deepcopy(state)
                            newState[i][j + 1] = "🖌️⬅️"
                            newState[i][j] = " "
                            result.append((f"({i},{j}) right", newState))
                    case "🖌️➡️":
                        if state[i - 1][j] == " ":
                            newState = copy.deepcopy(state)
                            newState[i - 1][j] = "🖌️➡️"
                            newState[i][j] = " "
                            result.append((f"({i},{j}) up", newState))
                        if state[i + 1][j] == " ":
                            newState = copy.deepcopy(state)
                            newState[i + 1][j] = "🖌️➡️"
                            newState[i][j] = " "
                            result.append((f"({i},{j}) down", newState))
                        if state[i][j - 1] == " ":
                            newState = copy.deepcopy(state)
                            newState[i][j - 1] = "🖌️➡️"
                            newState[i][j] = " "
                            result.append((f"({i},{j}) left", newState))
                        if state[i][j + 1] == " ":
                            newState = copy.deepcopy(state)
                            newState[i][j + 1] = "🖌️➡️"
                            newState[i][j] = " "
                            result.append((f"({i},{j}) right", newState))
                    case "🎨⬆️":
                        if state[i - 1][j] == " ":
                            newState = copy.deepcopy(state)
                            newState[i - 1][j] = "🎨⬆️"
                            newState[i][j] = " "
                            result.append((f"({i},{j}) up", newState))
                        if state[i + 1][j] == " ":
                            newState = copy.deepcopy(state)
                            newState[i + 1][j] = "🎨⬆️"
                            newState[i][j] = " "
                            result.append((f"({i},{j}) down", newState))
                        if state[i][j - 1] == " ":
                            newState = copy.deepcopy(state)
                            newState[i][j - 1] = "🎨⬆️"
                            newState[i][j] = " "
                            result.append((f"({i},{j}) left", newState))
                        if state[i][j + 1] == " ":
                            newState = copy.deepcopy(state)
                            newState[i][j + 1] = "🎨⬆️"
                            newState[i][j] = " "
                            result.append((f"({i},{j}) right", newState))
                    case "🎨⬇️":
                        if state[i - 1][j] == " ":
                            newState = copy.deepcopy(state)
                            newState[i - 1][j] = "🎨⬇️"
                            newState[i][j] = " "
                            result.append((f"({i},{j}) up", newState))
                        if state[i + 1][j] == " ":
                            newState = copy.deepcopy(state)
                            newState[i + 1][j] = "🎨⬇️"
                            newState[i][j] = " "
                            result.append((f"({i},{j}) down", newState))
                        if state[i][j - 1] == " ":
                            newState = copy.deepcopy(state)
                            newState[i][j - 1] = "🎨⬇️"
                            newState[i][j] = " "
                            result.append((f"({i},{j}) left", newState))
                        if state[i][j + 1] == " ":
                            newState = copy.deepcopy(state)
                            newState[i][j + 1] = "🎨⬇️"
                            newState[i][j] = " "
                            result.append((f"({i},{j}) right", newState))
                    case "🎨⬅️":
                        if state[i - 1][j] == " ":
                            newState = copy.deepcopy(state)
                            newState[i - 1][j] = "🎨⬅️"
                            newState[i][j] = " "
                            result.append((f"({i},{j}) up", newState))
                        if state[i + 1][j] == " ":
                            newState = copy.deepcopy(state)
                            newState[i + 1][j] = "🎨⬅️"
                            newState[i][j] = " "
                            result.append((f"({i},{j}) down", newState))
                        if state[i][j - 1] == " ":
                            newState = copy.deepcopy(state)
                            newState[i][j - 1] = "🎨⬅️"
                            newState[i][j] = " "
                            result.append((f"({i},{j}) left", newState))
                        if state[i][j + 1] == " ":
                            newState = copy.deepcopy(state)
                            newState[i][j + 1] = "🎨⬅️"
                            newState[i][j] = " "
                            result.append((f"({i},{j}) right", newState))
                    case "🎨➡️":
                        if state[i - 1][j] == " ":
                            newState = copy.deepcopy(state)
                            newState[i - 1][j] = "🎨➡️"
                            newState[i][j] = " "
                            result.append((f"({i},{j}) up", newState))
                        if state[i + 1][j] == " ":
                            newState = copy.deepcopy(state)
                            newState[i + 1][j] = "🎨➡️"
                            newState[i][j] = " "
                            result.append((f"({i},{j}) down", newState))
                        if state[i][j - 1] == " ":
                            newState = copy.deepcopy(state)
                            newState[i][j - 1] = "🎨➡️"
                            newState[i][j] = " "
                            result.append((f"({i},{j}) left", newState))
                        if state[i][j + 1] == " ":
                            newState = copy.deepcopy(state)
                            newState[i][j + 1] = "🎨➡️"
                            newState[i][j] = " "
                            result.append((f"({i},{j}) right", newState))
                    case "⬆️":
                        if state[i - 1][j] == " ":
                            newState = copy.deepcopy(state)
                            newState[i - 1][j] = "⬆️"
                            newState[i][j] = "⬇️"
                            newState[i + 1][j] = " "
                            result.append((f"({i},{j}) up", newState))
                        # Down can't be an empty space, it'll be the bottom half
                        if state[i][j - 1] == " ":
                            if state[i + 1][j - 1] == " ":
                                newState = copy.deepcopy(state)
                                newState[i][j - 1] = "⬆️"
                                newState[i + 1][j - 1] = "⬇️"
                                newState[i][j] = " "
                                newState[i + 1][j] = " "
                                result.append((f"({i},{j}) left", newState))
                        if state[i][j + 1] == " ":
                            if state[i + 1][j + 1] == " ":
                                newState = copy.deepcopy(state)
                                newState[i][j + 1] = "⬆️"
                                newState[i + 1][j + 1] = "⬇️"
                                newState[i][j] = " "
                                newState[i + 1][j] = " "
                                result.append((f"({i},{j}) right", newState))
                    case "⬇️":
                        # Up can't be an empty space, it'll be the top half
                        if state[i + 1][j] == " ":
                            newState = copy.deepcopy(state)
                            newState[i - 1][j] = " "
                            newState[i][j] = "⬆️"
                            newState[i + 1][j] = "⬇️"
                            result.append((f"({i},{j}) down", newState))
                        if state[i][j - 1] == " ":
                            if state[i - 1][j - 1] == " ":
                                newState = copy.deepcopy(state)
                                newState[i - 1][j - 1] = "⬆️"
                                newState[i][j - 1] = "⬇️"
                                newState[i - 1][j] = " "
                                newState[i][j] = " "
                                result.append((f"({i},{j}) left", newState))
                        if state[i][j + 1] == " ":
                            if state[i - 1][j + 1] == " ":
                                newState = copy.deepcopy(state)
                                newState[i - 1][j + 1] = "⬆️"
                                newState[i][j + 1] = "⬇️"
                                newState[i - 1][j] = " "
                                newState[i][j] = " "
                                result.append((f"({i},{j}) right", newState))
                    case "⬅️":
                        if state[i - 1][j] == " ":
                            if state[i - 1][j + 1] == " ":
                                newState = copy.deepcopy(state)
                                newState[i - 1][j] = "⬅️"
                                newState[i - 1][j + 1] = "➡️"
                                newState[i][j] = " "
                                newState[i][j + 1] = " "
                                result.append((f"({i},{j}) up", newState))
                        if state[i + 1][j] == " ":
                            if state[i + 1][j + 1] == " ":
                                newState = copy.deepcopy(state)
                                newState[i + 1][j] = "⬅️"
                                newState[i + 1][j + 1] = "➡️"
                                newState[i][j] = " "
                                newState[i][j + 1] = " "
                                result.append((f"({i},{j}) down", newState))
                        if state[i][j - 1] == " ":
                            newState = copy.deepcopy(state)
                            newState[i][j - 1] = "⬅️"
                            newState[i][j] = "➡️"
                            newState[i][j + 1] = " "
                            result.append((f"({i},{j}) left", newState))
                        # Right can't be an empty space, it'll be the right half
                    case "➡️":
                        if state[i - 1][j] == " ":
                            if state[i - 1][j - 1] == " ":
                                newState = copy.deepcopy(state)
                                newState[i - 1][j - 1] = "⬅️"
                                newState[i - 1][j] = "➡️"
                                newState[i][j - 1] = " "
                                newState[i][j] = " "
                                result.append((f"({i},{j}) up", newState))
                        if state[i + 1][j] == " ":
                            if state[i + 1][j - 1] == " ":
                                newState = copy.deepcopy(state)
                                newState[i + 1][j - 1] = "⬅️"
                                newState[i + 1][j] = "➡️"
                                newState[i][j - 1] = " "
                                newState[i][j] = " "
                                result.append((f"({i},{j}) down", newState))
                        # Left can't be an empty space, it'll be the left half
                        if state[i][j + 1] == " ":
                            newState = copy.deepcopy(state)
                            newState[i][j - 1] = " "
                            newState[i][j] = "⬅️"
                            newState[i][j + 1] = "➡️"
                            result.append((f"({i},{j}) left", newState))
                    case "❗⬆️":
                        if state[i - 1][j] == " ":
                            if not (
                                "❗" in state[i - 2][j]
                                or "❗" in state[i - 1][j - 1]
                                or "❗" in state[i - 1][j + 1]
                            ):
                                newState = copy.deepcopy(state)
                                newState[i - 1][j] = "❗⬆️"
                                newState[i][j] = "❗⬇️"
                                newState[i + 1][j] = " "
                                result.append((f"({i},{j}) up", newState))
                        # Down can't be an empty space, it'll be the bottom half
                        if state[i][j - 1] == " ":
                            if state[i + 1][j - 1] == " ":
                                if not (
                                    "❗" in state[i - 1][j - 1]
                                    or "❗" in state[i][j - 2]
                                    or "❗" in state[i + 1][j - 2]
                                    or "❗" in state[i + 2][j - 1]
                                ):
                                    newState = copy.deepcopy(state)
                                    newState[i][j - 1] = "❗⬆️"
                                    newState[i + 1][j - 1] = "❗⬇️"
                                    newState[i][j] = " "
                                    newState[i + 1][j] = " "
                                    result.append((f"({i},{j}) left", newState))
                        if state[i][j + 1] == " ":
                            if state[i + 1][j + 1] == " ":
                                if not (
                                    "❗" in state[i - 1][j + 1]
                                    or "❗" in state[i][j + 2]
                                    or "❗" in state[i + 1][j + 2]
                                    or "❗" in state[i + 2][j + 1]
                                ):
                                    newState = copy.deepcopy(state)
                                    newState[i][j + 1] = "❗⬆️"
                                    newState[i + 1][j + 1] = "❗⬇️"
                                    newState[i][j] = " "
                                    newState[i + 1][j] = " "
                                    result.append((f"({i},{j}) right", newState))
                    case "❗⬇️":
                        # Up can't be an empty space, it'll be the top half
                        if state[i + 1][j] == " ":
                            if not (
                                "❗" in state[i + 1][j - 1]
                                or "❗" in state[i + 2][j]
                                or "❗" in state[i + 1][j + 1]
                            ):
                                newState = copy.deepcopy(state)
                                newState[i - 1][j] = " "
                                newState[i][j] = "❗⬆️"
                                newState[i + 1][j] = "❗⬇️"
                                result.append((f"({i},{j}) down", newState))
                        if state[i][j - 1] == " ":
                            if state[i - 1][j - 1] == " ":
                                if not (
                                    "❗" in state[i - 2][j - 1]
                                    or "❗" in state[i - 1][j - 2]
                                    or "❗" in state[i][j - 2]
                                    or "❗" in state[i + 1][j - 1]
                                ):
                                    newState = copy.deepcopy(state)
                                    newState[i - 1][j - 1] = "❗⬆️"
                                    newState[i][j - 1] = "❗⬇️"
                                    newState[i - 1][j] = " "
                                    newState[i][j] = " "
                                    result.append((f"({i},{j}) left", newState))
                        if state[i][j + 1] == " ":
                            if state[i - 1][j + 1] == " ":
                                if not (
                                    "❗" in state[i - 2][j + 1]
                                    or "❗" in state[i - 1][j + 2]
                                    or "❗" in state[i][j + 2]
                                    or "❗" in state[i + 1][j + 1]
                                ):
                                    newState = copy.deepcopy(state)
                                    newState[i - 1][j + 1] = "❗⬆️"
                                    newState[i][j + 1] = "❗⬇️"
                                    newState[i - 1][j] = " "
                                    newState[i][j] = " "
                                    result.append((f"({i},{j}) right", newState))
                    case "❗⬅️":
                        if state[i - 1][j] == " ":
                            if state[i - 1][j + 1] == " ":
                                if not (
                                    "❗" in state[i - 1][j - 1]
                                    or "❗" in state[i - 2][j]
                                    or "❗" in state[i - 2][j + 1]
                                    or "❗" in state[i - 1][j + 2]
                                ):
                                    newState = copy.deepcopy(state)
                                    newState[i - 1][j] = "❗⬅️"
                                    newState[i - 1][j + 1] = "❗➡️"
                                    newState[i][j] = " "
                                    newState[i][j + 1] = " "
                                    result.append((f"({i},{j}) up", newState))
                        if state[i + 1][j] == " ":
                            if state[i + 1][j + 1] == " ":
                                if not (
                                    "❗" in state[i + 1][j - 1]
                                    or "❗" in state[i + 2][j]
                                    or "❗" in state[i + 2][j + 1]
                                    or "❗" in state[i + 1][j + 2]
                                ):
                                    newState = copy.deepcopy(state)
                                    newState[i + 1][j] = "❗⬅️"
                                    newState[i + 1][j + 1] = "❗➡️"
                                    newState[i][j] = " "
                                    newState[i][j + 1] = " "
                                    result.append((f"({i},{j}) down", newState))
                        if state[i][j - 1] == " ":
                            if not (
                                "❗" in state[i - 1][j - 1]
                                or "❗" in state[i][j - 2]
                                or "❗" in state[i + 1][j - 1]
                            ):
                                newState = copy.deepcopy(state)
                                newState[i][j - 1] = "❗⬅️"
                                newState[i][j] = "❗➡️"
                                newState[i][j + 1] = " "
                                result.append((f"({i},{j}) left", newState))
                        # Right can't be an empty space, it'll be the right half
                    case "❗➡️":
                        if state[i - 1][j] == " ":
                            if state[i - 1][j - 1] == " ":
                                if not (
                                    "❗" in state[i - 1][j - 2]
                                    or "❗" in state[i - 2][j - 1]
                                    or "❗" in state[i - 2][j]
                                    or "❗" in state[i - 1][j + 1]
                                ):
                                    newState = copy.deepcopy(state)
                                    newState[i - 1][j - 1] = "❗⬅️"
                                    newState[i - 1][j] = "❗➡️"
                                    newState[i][j - 1] = " "
                                    newState[i][j] = " "
                                    result.append((f"({i},{j}) up", newState))
                        if state[i + 1][j] == " ":
                            if state[i + 1][j - 1] == " ":
                                if not (
                                    "❗" in state[i + 1][j - 2]
                                    or "❗" in state[i + 2][j - 1]
                                    or "❗" in state[i + 2][j]
                                    or "❗" in state[i + 1][j + 1]
                                ):
                                    newState = copy.deepcopy(state)
                                    newState[i + 1][j - 1] = "❗⬅️"
                                    newState[i + 1][j] = "❗➡️"
                                    newState[i][j - 1] = " "
                                    newState[i][j] = " "
                                    result.append((f"({i},{j}) down", newState))
                        # Left can't be an empty space, it'll be the left half
                        if state[i][j + 1] == " ":
                            if not (
                                "❗" in state[i - 1][j + 1]
                                or "❗" in state[i][j + 2]
                                or "❗" in state[i + 1][j + 1]
                            ):
                                newState = copy.deepcopy(state)
                                newState[i][j - 1] = " "
                                newState[i][j] = "❗⬅️"
                                newState[i][j + 1] = "❗➡️"
                                result.append((f"({i},{j}) left", newState))

        # Comment the line below to hide AI search text from terminal
        print(f"Result: {result}")
        return result

    def solve(self):
        """Finds a solution to puzzle, if one exists."""

        # Keep track of number of states explored
        self.num_explored = 0

        # Initialize frontier to just the starting position
        start = Node(state=self.start, parent=None, action=None)
        frontier = QueueFrontier()
        frontier.add(start)

        # Initialize an empty explored set
        self.explored = []

        # Keep looping until solution found
        while True:

            # If nothing left in frontier, then no path
            if frontier.empty():
                raise Exception(Color.RED + "No solution possible" + Color.ENDC)

            # Choose a node from the frontier
            node = frontier.remove()
            self.num_explored += 1

            # If node is the goal, then we have a solution
            goal = False
            for i in range(self.height):
                for j in range(self.width):
                    if "🖌️" in node.state[i][j]:
                        match node.state[i][j]:
                            case "🖌️⬆️":
                                if node.state[i - 1][j] == "🎨⬇️":
                                    goal = True
                            case "🖌️⬇️":
                                if node.state[i + 1][j] == "🎨⬆️":
                                    goal = True
                            case "🖌️⬅️":
                                if node.state[i][j - 1] == "🎨➡️":
                                    goal = True
                            case "🖌️➡️":
                                if node.state[i][j + 1] == "🎨⬅️":
                                    goal = True
            if goal:
                actions = []
                cells = []
                while node.parent is not None:
                    actions.append(node.action)
                    cells.append(node.state)
                    node = node.parent
                actions.reverse()
                cells.reverse()
                self.solution = (actions, cells)
                return

            # Mark node as explored
            self.explored.append(node.state)

            # Add neighbors to frontier
            for action, state in self.neighbors(node.state):
                if not frontier.contains_state(state) and state not in self.explored:
                    child = Node(state=state, parent=node, action=action)
                    frontier.add(child)


# Terminal display
def placeEmoji(grid, x, y, emoji):
    if (grid[x][y]) != " " and emoji != " ":
        raise Exception(Color.RED + "Occupied space" + Color.ENDC)
    else:
        grid[x][y] = emoji


def printGrid(grid):
    line = "  "
    for j in range(int(columns)):
        line += "  " + chr(ord("A") + j)
    print(line)
    line = "   ┌"
    for j in range(int(columns) - 1):
        line += "──┬"
    line += "──┐"
    print(line)
    dividerLine = "   │"
    for j in range(int(columns)):
        dividerLine += "──│"
    for i in range(int(rows)):
        line = str(i + 1) + "  │"
        for j in range(int(columns)):
            if grid[i][j] == " ":
                line += "  │"
            else:
                if "🖌️" in grid[i][j]:
                    line += "🖌️ │"
                elif "🎨" in grid[i][j]:
                    line += "🎨│"
                elif "❗" in grid[i][j] and len(grid[i][j]) > 1:
                    line += "❕│"
                elif grid[i][j] == "⬆️" or grid[i][j] == "⬇️" or grid[i][j] == "⬅️" or grid[i][j] == "➡️":
                    line += grid[i][j] + " │"
                else:
                    line += grid[i][j] + "│"
        print(line)
        if i < int(rows) - 1:
            print(dividerLine)
    line = "   └"
    for j in range(int(columns) - 1):
        line += "──┴"
    line += "──┘"
    print(line)


rows = input("How many rows are in your puzzle?\n")
columns = input("How many columns are in your puzzle?\n")
puzzleGrid = [[" " for _ in range(int(columns))] for _ in range(int(rows))]

printGrid(puzzleGrid)
stillSetup = True
while stillSetup:
    blockNum = int(
        input(
            f"Which block do you want to place?\n    {Color.BOLD}{Color.GREEN}1{Color.ENDC}. {Color.GRAY}Immovable Block\n    {Color.BOLD}{Color.GREEN}2{Color.ENDC}. {Color.BLUE}Movable Block\n    {Color.BOLD}{Color.GREEN}3{Color.ENDC}. {Color.RED}Boom Block\n    {Color.BOLD}{Color.GREEN}4{Color.ENDC}. {Color.GREEN}Horizontal Directional Block\n    {Color.BOLD}{Color.GREEN}5{Color.ENDC}. {Color.GREEN}Vertical Directional Block\n    {Color.BOLD}{Color.GREEN}6{Color.ENDC}. {Color.YELLOW}Light Block\n    {Color.BOLD}{Color.GREEN}7{Color.ENDC}. {Color.MAGENTA}Dye Injector Block\n    {Color.BOLD}{Color.GREEN}8{Color.ENDC}. {Color.MAGENTA}Dye Receiver Block\n    {Color.BOLD}{Color.GREEN}9{Color.ENDC}. {Color.BLUE}Double Movable Block\n    {Color.BOLD}{Color.GREEN}10{Color.ENDC}. {Color.RED}Double Boom Block\n    {Color.BOLD}{Color.GREEN}11{Color.ENDC}. Empty Space{Color.ENDC}\n"
        )
    )
    if blockNum > 10 or blockNum < 1:
        raise Exception(Color.RED + "Index out of range" + Color.ENDC)
    emoji = ""
    match blockNum:
        case 1:
            emoji = "⬛"
        case 2:
            emoji = "🟦"
        case 3:
            emoji = "❗"
        case 4:
            emoji = "🔄"
        case 5:
            emoji = "🔃"
        case 6:
            emoji = "⚡"
        case 7:
            direction = int(
                input(
                    f"Which way is the {Color.MAGENTA}Injector{Color.ENDC} facing?\n    {Color.BOLD}{Color.GREEN}1{Color.ENDC}. North\n    {Color.BOLD}{Color.GREEN}2{Color.ENDC}. South\n    {Color.BOLD}{Color.GREEN}3{Color.ENDC}. East\n    {Color.BOLD}{Color.GREEN}4{Color.ENDC}. West\n"
                )
            )
            if direction > 4 or direction < 1:
                raise Exception(Color.RED + "Index out of range" + Color.ENDC)
            match direction:
                case 1:
                    emoji = "🖌️⬆️"
                case 2:
                    emoji = "🖌️⬇️"
                case 3:
                    emoji = "🖌️⬅️"
                case 4:
                    emoji = "🖌️➡️"
        case 8:
            direction = int(
                input(
                    f"Which way is the {Color.MAGENTA}Receiver{Color.ENDC} facing?\n    {Color.BOLD}{Color.GREEN}1{Color.ENDC}. North\n    {Color.BOLD}{Color.GREEN}2{Color.ENDC}. South\n    {Color.BOLD}{Color.GREEN}3{Color.ENDC}. East\n    {Color.BOLD}{Color.GREEN}4{Color.ENDC}. West\n"
                )
            )
            if direction > 4 or direction < 1:
                raise Exception(Color.RED + "Index out of range" + Color.ENDC)
            match direction:
                case 1:
                    emoji = "🎨⬆️"
                case 2:
                    emoji = "🎨⬇️"
                case 3:
                    emoji = "🎨⬅️"
                case 4:
                    emoji = "🎨➡️"
        case 9:
            direction = int(
                input(
                    f"Which way is the {Color.BLUE}Double Movable Block{Color.ENDC} facing?\n    {Color.BOLD}{Color.GREEN}1{Color.ENDC}. Vertical\n    {Color.BOLD}{Color.GREEN}2{Color.ENDC}. Horizontal\n"
                )
            )
            if direction > 2 or direction < 1:
                raise Exception(Color.RED + "Index out of range" + Color.ENDC)
            match direction:
                case 1:
                    emoji = "⬆️"
                case 2:
                    emoji = "⬅️"
        case 10:
            direction = int(
                input(
                    f"Which way is the {Color.RED}Double Boom Block{Color.ENDC} facing?\n    {Color.BOLD}{Color.GREEN}1{Color.ENDC}. Vertical\n    {Color.BOLD}{Color.GREEN}2{Color.ENDC}. Horizontal\n"
                )
            )
            if direction > 2 or direction < 1:
                raise Exception(Color.RED + "Index out of range" + Color.ENDC)
            match direction:
                case 1:
                    emoji = "❗⬆️"
                case 2:
                    emoji = "❗⬅️"
        case 11:
            emoji = " "
    printGrid(puzzleGrid)
    coord = input(
        f"Where would you like to place this block? ({Color.UNDERLINE}{Color.GREEN}e.g. a1{Color.ENDC})\nFor double blocks, this would be the coordinate for the top or left half\n"
    ).lower()
    line = ""
    for j in range(int(columns)):
        line += chr(ord("A") + j)
    if not (coord[:1].lower() in line.lower()) or int(coord[1:]) < 1:
        raise Exception(Color.RED + "Index out of range" + Color.ENDC)
    placeEmoji(puzzleGrid, int(coord[1:]) - 1, ord(coord[:1]) - 97, emoji)
    if emoji == "⬆️":
        placeEmoji(puzzleGrid, int(coord[1:]), ord(coord[:1]) - 97, "⬇️")
    elif emoji == "⬅️":
        placeEmoji(puzzleGrid, int(coord[1:] - 1), ord(coord[:1]) - 96, "➡️")
    elif emoji == "❗⬆️":
        placeEmoji(puzzleGrid, int(coord[1:]), ord(coord[:1]) - 97, "❗⬇️")
    elif emoji == "❗⬅️":
        placeEmoji(puzzleGrid, int(coord[1:] - 1), ord(coord[:1]) - 96, "❗➡️")

    printGrid(puzzleGrid)
    startSearch = input(
        f"Start search? {Color.UNDERLINE}{Color.GREEN}y{Color.ENDC}/{Color.RED}n{Color.ENDC}\n"
    ).lower()
    if startSearch != "y" and startSearch != "n":
        raise Exception(Color.RED + "Option unavailable" + Color.ENDC)
    if startSearch == "y":
        stillSetup = False

newGrid = [
    ["⬛" for _ in range(len(puzzleGrid[0]) + 2)] for _ in range(len(puzzleGrid) + 2)
]
for i in range(len(puzzleGrid)):
    for j in range(len(puzzleGrid[0])):
        newGrid[i + 1][j + 1] = puzzleGrid[i][j]

p = Puzzle(newGrid)
timerStart = time.time()
p.solve()
timerEnd = time.time()
print(
    f"\n{Color.BOLD}{Color.UNDERLINE}{Color.GREEN}States explored{Color.ENDC}: {p.num_explored}\n"
)
print(
    f"{Color.BOLD}{Color.UNDERLINE}{Color.GREEN}Ideal move count{Color.ENDC}: {len(p.solution[0])}\n"
)
print(
    f"{Color.BOLD}{Color.UNDERLINE}{Color.GREEN}Solution{Color.ENDC}: {p.solution[0]}\n"
)
print(
    f"{Color.BOLD}{Color.UNDERLINE}{Color.GREEN}Solution found in{Color.ENDC}: {int((timerEnd-timerStart)/60)}m {int((timerEnd-timerStart)%60)}s\n"
)


displayMoves = input(
    f"Display moves in terminal? {Color.UNDERLINE}{Color.GREEN}y{Color.ENDC}/{Color.RED}n{Color.ENDC}\n"
).lower()
if displayMoves != "y" and displayMoves != "n":
    raise Exception(Color.RED + "Option unavailable" + Color.ENDC)
if displayMoves == "y":
    displayMoves = True
i = 0
while displayMoves and i < len(p.solution[1]):
    tempGrid = [
        [" " for _ in range(len(p.solution[1][0][0]) - 2)]
        for _ in range(len(p.solution[1][0]) - 2)
    ]
    for x in range(len(tempGrid)):
        for y in range(len(tempGrid[0])):
            tempGrid[x][y] = p.solution[1][i][x + 1][y + 1]
    print(f"Move {i+1}:")
    printGrid(tempGrid)
    if i + 1 == len(p.solution[0]):
        print(f"{Color.BOLD}{Color.GREEN}Solution reached{Color.ENDC}")
        displayMoves = False
    else:
        keepGoing = input(
            f"Press any key to keep going, or {Color.UNDERLINE}{Color.GREEN}q{Color.ENDC} to quit\n"
        ).lower()
        if keepGoing == "q":
            displayMoves = False
    i += 1
