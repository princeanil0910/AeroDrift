import ast


def generate_remediation_code(security_group, source):
    """
    Generate Python remediation code dynamically.
    """

    code = f'''
def remediate():
    revoke_public_access(
        security_group="{security_group}",
        source="{source}"
    )
'''

    return code.strip()


def validate_remediation_code(code):
    """
    Validate generated remediation code using Python AST.
    """

    try:
        tree = ast.parse(code)

        has_function = any(
            isinstance(node, ast.FunctionDef)
            and node.name == "remediate"
            for node in tree.body
        )

        if has_function:
            return True, "AST validation successful"

        return False, "remediate() function not found"

    except SyntaxError as error:
        return False, f"Invalid Python code: {error}"