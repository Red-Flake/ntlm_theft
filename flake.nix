{
  description = "Generate multiple types of NTLMv2 hash theft files";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs =
    { self, nixpkgs }:
    let
      supportedSystems = [
        "x86_64-linux"
        "aarch64-linux"
        "x86_64-darwin"
        "aarch64-darwin"
      ];
      forAllSystems = nixpkgs.lib.genAttrs supportedSystems;
    in
    {
      packages = forAllSystems (system: {
        ntlm_theft = nixpkgs.legacyPackages.${system}.callPackage ./default.nix { };
        default = self.packages.${system}.ntlm_theft;
      });

      devShells = forAllSystems (system: {
        default = nixpkgs.legacyPackages.${system}.mkShell {
          packages = [
            (nixpkgs.legacyPackages.${system}.python3.withPackages (ps: [ ps.xlsxwriter ]))
          ];
        };
      });
    };
}
