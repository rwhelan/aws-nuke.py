

def dependency_sort(module_list):
    L = []
    visited = []

    def nodeps(module_list):
        S = []
        for each in module_list:
            if not len(each.dependencies):
                S.append(each)
        return S

    def dependson(node):
        r = []
        for each in module_list:
            for n in each.dependencies:
                if n == node.name:
                    r.append(each)
        return r

    def visit(node):
        if node.name not in visited:
            visited.append(node.name)
            for m in dependson(node):
                visit(m)
            L.append(node)

    for node in nodeps(module_list):
        visit(node)

    return L[::-1]
