{
  lib,
  stdenv,
  python3,
  makeWrapper,
  dos2unix,
}:

let
  pythonEnv = python3.withPackages (ps: [ ps.xlsxwriter ]);
in
stdenv.mkDerivation {
  pname = "ntlm_theft";
  version = "0-unstable-2024-01-15";

  src = lib.fileset.toSource {
    root = ./.;
    fileset = lib.fileset.unions [
      ./ntlm_theft.py
      ./templates
      ./nix/fix-nix-store-copy.patch
    ];
  };

  nativeBuildInputs = [
    dos2unix
    makeWrapper
  ];

  prePatch = ''
    dos2unix ntlm_theft.py
    find templates -type f \( -name "*.xml" -o -name "*.rels" \) -exec dos2unix {} \;
  '';

  patches = [ ./nix/fix-nix-store-copy.patch ];

  dontBuild = true;

  installPhase = ''
    runHook preInstall

    install -Dm755 ntlm_theft.py $out/share/ntlm_theft/ntlm_theft.py
    cp -r templates $out/share/ntlm_theft/

    makeWrapper ${pythonEnv}/bin/python $out/bin/ntlm_theft \
      --add-flags "$out/share/ntlm_theft/ntlm_theft.py"

    runHook postInstall
  '';

  meta = {
    description = "Generate multiple types of NTLMv2 hash theft files";
    homepage = "https://github.com/Greenwolf/ntlm_theft";
    license = lib.licenses.gpl3Only;
    maintainers = with lib.maintainers; [ ];
    mainProgram = "ntlm_theft";
    platforms = lib.platforms.all;
  };
}
