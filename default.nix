{ python3Packages, lib }:

python3Packages.buildPythonApplication {
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

  meta = {
    description = "a simple script to generate mock class code for C++";
    homepage = "https://github.com/yaoshiu/drygmock";
    license = lib.licenses.mit;
    maintainers = [
      {
        email = "akafayash@icloud.com";
        name = "Fay Ash";
        github = "yaoshiu";
        githubId = 56054933;
      }
    ];
    platforms = lib.platforms.all;
  };
}
