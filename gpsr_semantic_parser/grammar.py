from copy import deepcopy

from gpsr_semantic_parser.util import replace_child

from gpsr_semantic_parser.tokens import  *

from lark import Tree, Transformer, Visitor


class TypeConverter(Transformer):
    def non_terminal(self, children):
        return NonTerminal(children[0])

    def wildcard(self, children):
        typed = children[0]
        type = typed.children[0] if len(typed.children) > 0 else None
        extra = typed.children[1] if len(typed.children) > 1 else None
        if "obj" in typed.data:
            if "alike" in typed.data:
                type = "alike"
                extra = typed.children[0] if len(typed.children) > 1 else None
            elif "known" in typed.data:
                type = "known"
                extra = typed.children[0] if len(typed.children) > 1 else None
            return WildCard("object", type, extra)
        elif "loc" in typed.data:
            if "beacon" in typed.data:
                type = "beacon"
                extra = typed.children[0] if len(typed.children) > 1 else None
            elif "placement" in typed.data:
                type ="placement"
                extra = typed.children[0] if len(typed.children) > 1 else None
            elif "room" in typed.data:
                type = "room"
                extra = typed.children[0] if len(typed.children) > 1 else None
            return WildCard("location", type, extra)
        elif "category" in typed.data:
            return WildCard("category", type)
        elif "gesture" in typed.data:
            return WildCard("gesture", type)
        elif "name" in typed.data:
            return WildCard("name", type)
        elif "pron" in typed.data:
            return WildCard("pron", type)
        elif "question" in typed.data:
            return WildCard("question", type)
        elif "void" in typed.data:
            return WildCard("void", type)
        elif "whattosay" in typed.data:
            return WildCard("whattosay")
        assert False


class DiscardVoid(Visitor):
    def expression(self, tree):
        tree.children = list(filter(lambda x: not ((isinstance(x, WildCard) or isinstance(x, Anonymized)) and x.name == "void"), tree.children))





class ToString(Transformer):
    def __default__(self, data, children, meta):
        return " ".join(map(str, children))

    def non_terminal(self, children):
        return "${}".format(" ".join(children))

    def choice(self, children):
        output = "("
        for child in children:
            output += child + " | "
        return output[:-3] + ")"

    def rule(self, children):
        return "{} = {}".format(children[0], children[1])

    def predicate(self, children):
        # Check for any string constant args and make sure they have
        # padding spaces between text and the quote marks
        for i, child in enumerate(children):
            if  isinstance(child, str) and child[0] == "\"":
                children[i] = "\" " + child[1:-1] + " \""
        return "( {} )".format(" ".join(map(str,children)))

    def lambda_abs(self, children):
        return "( lambda {} )".format(" ".join(map(str,children)))

    def constant_placeholder(self, children):
        return "\"" + " ".join(children) + "\""

    def __call__(self, *args, **kwargs):
        return self.transform(*args)


tree_printer = ToString()


class CombineExpressions(Visitor):
    """
    Grammars may generate multiple text fragments in a sequence. This will combine them
    :param tokens:
    :return: a list of tokens with no adjacent text fragments
    """
    def top_expression(self, tree):
        tree.data = "expression"
        self.expression(tree)

    def expression(self, tree):
        cleaned = []
        i = 0
        while i < len(tree.children):
            child = tree.children[i]
            # Not a fragment? Forward to output
            if not (isinstance(child, Tree) and child.data == "expression"):
                cleaned.append(child)
                i += 1
                continue
            # Otherwise, gather up the the next subsequence of fragments
            j = i + 1
            while j < len(tree.children):
                next_child = tree.children[j]
                if isinstance(next_child, Tree) and next_child.data == "expression":
                    j += 1
                    continue
                break
            cleaned.extend([c for t in tree.children[i:j] for c in t.children])
            i = j
        if i == len(tree.children) - 1:
            cleaned.append(tree.children[i])

        all_expanded = False
        while not all_expanded:
            i = 0
            while i < len(cleaned):
                child = cleaned[i]
                if isinstance(child, Tree) and child.data == "expression":
                    cleaned = cleaned[:i] + child.children + cleaned[i+1:]
                    break
                i += 1
            all_expanded = True
        tree.children = cleaned


def expand_shorthand(tree):
    in_progress = [tree]
    output = []
    while len(in_progress) != 0:
        current = in_progress.pop()
        choices = list(current.find_data("choice"))
        if len(choices) == 0:
            output.append(current)
            continue
        for choice in choices:
            for option in choice.children:
                choice_made_tree = deepcopy(tree)
                if choice_made_tree == choice:
                    in_progress.append(option)
                else:
                    choice_parent = list(choice_made_tree.find_pred(lambda subtree: any([child == choice for child in subtree.children])))[0]
                    replace_child(choice_parent, choice, option, only_once=True)
                    in_progress.append(choice_made_tree)

    return output
