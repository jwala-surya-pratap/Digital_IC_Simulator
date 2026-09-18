{
  description = "Python virtual environment Nix flake";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs =
    { self, nixpkgs }:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs { inherit system; };
      python = pkgs.python311;

      # Define graphics/display libraries needed by SDL2/PyGame
      runtimeLibs = with pkgs; [
        zlib
        SDL2
        SDL2_image
        SDL2_mixer
        SDL2_ttf
        libGL
        wayland
        libX11
        libXext
        libXcursor
        libXrandr
        libXi
        libXinerama
      ];
    in
    {
      devShells.${system}.default = pkgs.mkShell {
        buildInputs = [
          python
          python.pkgs.pip
          python.pkgs.virtualenv
          python.pkgs.pytest
        ]
        ++ runtimeLibs;

        shellHook = ''
          # Expose C libraries to dynamic loader for pip packages
          export LD_LIBRARY_PATH="${pkgs.lib.makeLibraryPath runtimeLibs}:$LD_LIBRARY_PATH"

          VENV=.venv
          if [ ! -d "$VENV" ]; then
            echo "Creating virtual environment in $VENV..."
            ${python}/bin/python -m venv $VENV
          fi

          source $VENV/bin/activate

          # Ensure pip installs within the virtual environment
          export PIP_PREFIX="$(pwd)/$VENV"
          export PATH="$PIP_PREFIX/bin:$PATH"

          echo "Python dev shell ready. Active Python: $(which python)"
        '';
      };
    };
}
