# To learn more about how to use Nix to configure your environment
# see: https://developers.google.com/idx/guides/customize-idx-env
{ pkgs, ... }: {
  # Which nixpkgs channel to use.
  channel = "stable-24.11"; # or "unstable"

  # Use https://search.nixos.org/packages to find packages
  packages = [
    (pkgs.python3.withPackages (python-pkgs: [
      python-pkgs.numpy
      python-pkgs.pandas
      python-pkgs.jsonschema
      (python-pkgs.xlrd.overrideAttrs(_: { version = "1.2.0"; }))
      python-pkgs.openpyxl
      python-pkgs.pytest
      python-pkgs.matplotlib
    ]))
    # for libraries written in C/C++ such as numpy and pandas, installed by poetry
    # pkgs.libz
    # pkgs.gcc
    # pkgs.nix-ld
  ];

  # Sets environment variables in the workspace
  env = {
    # for libraries written in C/C++ such as numpy and pandas, installed by poetry
    # NIX_LD_LIBRARY_PATH = lib.makeLibraryPath [
    #   pkgs.stdenv.cc.cc
    #   pkgs.libz
    #   pkgs.gcc
    # ];
  };
  idx = {
    # Search for the extensions you want on https://open-vsx.org/ and use "publisher.id"
    extensions = [
      "ms-python.debugpy"
      "ms-python.python"
    ];

    # Enable previews
    previews = {
      enable = true;
      previews = {
        # web = {
        #   # Example: run "npm run dev" with PORT set to IDX's defined port for previews,
        #   # and show it in IDX's web preview panel
        #   command = ["npm" "run" "dev"];
        #   manager = "web";
        #   env = {
        #     # Environment variables to set for your server
        #     PORT = "$PORT";
        #   };
        # };
      };
    };

    # Workspace lifecycle hooks
    workspace = {
      # Runs when a workspace is first created
      onCreate = {};
      # Runs when the workspace is (re)started
      onStart = {};
    };
  };
}
