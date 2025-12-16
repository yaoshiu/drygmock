import argparse
from tree_sitter import Parser, Language, Tree, Node
from tree_sitter_cpp import language
from pathlib import Path
from typing import Generator


def parse_file(path: str) -> tuple[Tree, bytes]:
    parser = Parser(language=Language(language()))
    source = Path(path).read_bytes()
    tree = parser.parse(source)
    return tree, source


def find_classes(node: Node) -> Generator[Node]:
    if node.type in ("class_specifier", "struct_specifier"):
        yield node
    for c in node.children:
        yield from find_classes(c)


def is_pure_virtual(method: Node) -> bool:
    has_virtual = any(c.type == "virtual" for c in method.children)
    has_equal = False
    has_pure = False
    for c in method.children:
        if c.type == "=":
            has_equal = True
        elif has_equal:
            if c.type == "number_literal":
                has_pure = True
            else:
                has_equal = False
    return has_virtual and has_pure


def get_method_name(method: Node, source: bytes) -> str | None:
    for c in method.children:
        if c.type == "function_declarator":
            for d in c.children:
                if d.type in ("identifier", "field_identifier"):
                    return source[d.start_byte : d.end_byte].decode()


def get_return_type(method: Node, source: bytes) -> str | None:
    for c in method.children:
        if c.type in (
            "type_identifier",
            "primitive_type",
            "qualified_identifier",
        ):
            return source[c.start_byte : c.end_byte].decode()


def get_params(method: Node, source: bytes) -> list[str]:
    params = []
    for f in method.children:
        if f.type == "function_declarator":
            for c in f.children:
                if c.type == "parameter_list":
                    for p in c.children:
                        if p.type == "parameter_declaration":
                            params.append(source[p.start_byte : p.end_byte].decode())
    return params


def is_const(method: Node) -> bool:
    return any(c.type == "const" for c in method.children)


def method_info(
    method: Node, source: bytes
) -> dict[str, str | None | bool | list[str]]:
    return {
        "name": get_method_name(method, source),
        "return": get_return_type(method, source),
        "params": get_params(method, source),
        "const": is_const(method),
    }


def need_parenthesis(param: str) -> bool:
    return ", " in param and not param.strip().startswith("(")


def gen_mock(m):
    ret = m["return"]
    name = m["name"]
    params = ", ".join(f"({p})" if need_parenthesis(p) else p for p in m["params"])
    qualifiers = []
    if m["const"]:
        qualifiers.append("const")
    qualifiers.append("override")
    return f"MOCK_METHOD({ret}, {name}, ({params}), ({', '.join(qualifiers)}));"


def gen_mock_class(cls: Node, source: bytes):
    class_name = None
    for c in cls.children:
        if c.type == "type_identifier":
            class_name = source[c.start_byte : c.end_byte].decode()

    methods = [
        gen_mock(method_info(m, source))
        for c in cls.children
        for m in c.children
        if m.type
        in (
            "function_definition",
            "function_declaration",
            "field_declaration",
            "field_definition",
        )
        and is_pure_virtual(m)
    ]

    if methods:
        print(f"class Mock{class_name} : public {class_name} {{")
        print("public:")
        for m in methods:
            print(f"  {m}")
        print("};")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("header")
    args = parser.parse_args()

    tree, source = parse_file(args.header)

    for cls in find_classes(tree.root_node):
        gen_mock_class(cls, source)


if __name__ == "__main__":
    main()
