{
  description = "Resolve and print absolute paths of dynamic dependencies using ldd";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs =
    {
      self,
      nixpkgs,
      flake-utils,
      ...
    }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        ldd-paths =
          pkgs.runCommand "ldd-paths"
            {
              buildInputs = [ pkgs.python3 ];
            }
            ''
              mkdir -p $out/bin
              cp ${self}/ldd-paths.py $out/bin/ldd-paths
              chmod +x $out/bin/ldd-paths
            '';
      in
      {
        packages.default = ldd-paths;

        devShells.default = pkgs.mkShell {
          buildInputs = [
            ldd-paths
          ];
        };
      }
    );
}
