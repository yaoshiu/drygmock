{ python3Packages, pkg-config, libclang }:

python3Packages.buildPythonApplication rec {
  pname = "drygmock";
  version = "0.1.0";
  pyproject = true;

  src = ./.;

  build-system = with python3Packages; [ setuptools ];

  dependencies = with python3Packages; [
    libclang
    tree-sitter
    tree-sitter-grammars.tree-sitter-cpp
  ];

  buildInputs = [
    libclang
  ];

  nativeBuildInputs = [
    pkg-config
  ];
}
