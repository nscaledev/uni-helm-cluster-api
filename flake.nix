{
  description = "uni-helm-cluster-api development environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        pythonEnv = pkgs.python3.withPackages (ps: [ ps.pyyaml ]);
      in {
        devShells.default = pkgs.mkShell {
          packages = [
            pythonEnv
            pkgs.kubectl
            pkgs.kubernetes-helm
            pkgs.go
            pkgs.gnumake
          ];
          shellHook = ''
            export PYTHONPATH="${pythonEnv}/${pkgs.python3.sitePackages}:''${PYTHONPATH:-}"
          '';
        };
      });
}
