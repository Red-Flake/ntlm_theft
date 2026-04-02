{
  lib,
  stdenv,
  fetchFromGitHub,
  python3,
  makeWrapper,
  dos2unix,
}:

let
  pythonEnv = python3.withPackages (ps: [ ps.xlsxwriter ]);
in
stdenv.mkDerivation rec {
  pname = "ntlm_theft";
  version = "0-unstable-2024-01-15";

  src = fetchFromGitHub {
    owner = "Greenwolf";
    repo = "ntlm_theft";
    rev = "9750e537444a411e99555155b3a32fad745ae3d4";
    hash = "sha256-wahjAokAbOa9gpiLO77ZgMaqWCOH34oJBrbEqgoxz8E=";
  };

  nativeBuildInputs = [
    dos2unix
    makeWrapper
  ];

  prePatch = ''
    dos2unix ntlm_theft.py
    find templates -type f \( -name "*.xml" -o -name "*.rels" \) -exec dos2unix {} \;
  '';

  patches = [ ./fix-nix-store-copy.patch ];

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
