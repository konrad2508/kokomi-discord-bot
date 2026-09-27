{
  description = "Dev shell for kokomi-discord-bot";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-26.05";
    flake-parts.url = "github:hercules-ci/flake-parts";
  };

  outputs = { flake-parts, ... } @ inputs: 
    flake-parts.lib.mkFlake { inherit inputs; } {
      systems = [ "x86_64-linux" "aarch64-linux" "x86_64-darwin" "aarch64-darwing" ];

      perSystem = { pkgs, ... }: {
        devShells.default = pkgs.mkShell {
          packages = with pkgs; [
            gnumake
            python3
            uv
          ];

          env = {
            UV_CACHE_DIR = ".venv-cache";
          };

          shellHook = ''
            if [ ! -d .venv ]; then
              uv venv .venv
            fi

            source .venv/bin/activate

            uv pip install -r requirements.txt
          '';
        };
      };
    };
}
