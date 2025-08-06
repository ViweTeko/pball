nix
# flake.nix
{
  description = "Your Powerball Project";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable"; # You can use a specific channel or commit
  };

  outputs = { self, nixpkgs, ... }: {
    devShells.default = nixpkgs.lib.evalModules {
      modules = [
        {
          nixpkgs.overlays = [
            self.overlays.default
          ];
        }
        ./.idx/dev.nix # Import your existing dev.nix
      ];
      specialArgs = { inherit self nixpkgs; };
    };

    # You can define other outputs here, like packages or applications

    overlays.default = final: prev: {
      # You can add custom packages or modify existing ones here if needed
    };
  };
}