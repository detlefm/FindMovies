────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│  > Kann ich das Container Image auch in meinem Github Repo speichern oder anderweitig verteilen oder macht   │
│    man sowas nicht                                                                                           │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

✦ Das ist eine ausgezeichnete Frage, und Ihr Instinkt ist richtig: Man speichert Docker-Images nicht direkt in
  einem Git-Repository wie GitHub.

  Hier ist die Erklärung, warum das so ist, und wie man es stattdessen richtig macht.

  Warum keine Images in Git speichern?

   1. Git ist für Source Code, nicht für Binärdateien: Git ist darauf optimiert, textbasierte Dateien (Ihren
      Quellcode) zu verwalten. Es kann Änderungen zeilenweise verfolgen und ist darin extrem effizient.
      Docker-Images sind große, komprimierte Binärdateien.
   2. Enorme Größe: Ein Git-Repository würde durch die Images auf viele hundert Megabyte oder sogar Gigabyte
      anwachsen. Jeder git clone würde ewig dauern.
   3. Ineffiziente Speicherung: Git speichert Versionen von Dateien. Bei jeder kleinen Änderung am Image würde Git
      eine weitere riesige Binärdatei speichern müssen, was das Repository schnell unbrauchbar macht.

  ---

  Der richtige Weg: Container Registries

  Die Standardlösung für das Speichern und Verteilen von Docker-Images sind Container Registries.

  Eine Registry ist ein spezielles Speichersystem und eine Verteilungsplattform für Container-Images. Wenn Git
  das "Bücherregal für Ihre Kochrezepte" (Source Code) ist, dann ist eine Container Registry das "Lagerhaus für
  Ihre fertigen Backmischungen" (Images).

  Ihre beste Option: GitHub Container Registry (GHCR)

  Da Sie bereits GitHub verwenden, ist die GitHub Container Registry die perfekte Lösung für Sie. Sie ist direkt
  in Ihr Repository integriert.

  Vorteile:
   * Direkt bei Ihrem Code: Die Images sind logisch mit dem Repository verknüpft, das sie erstellt hat.
   * Berechtigungen: Sie können die gleichen Berechtigungen wie für Ihr Repository verwenden.
   * Kostenlos (für öffentliche Repos): Für öffentliche Repositories ist die Nutzung kostenlos.

  Workflow zum Verteilen über GHCR:

   1. Authentifizieren Sie Docker bei GHCR:
      Sie müssen sich mit Ihrem GitHub-Benutzernamen und einem Personal Access Token (PAT) mit read:packages und
  write:packages Rechten anmelden. Verwenden Sie nicht Ihr normales Passwort!

   1     # Erstellen Sie ein PAT in Ihren GitHub-Entwicklereinstellungen
   2     export CR_PAT="YOUR_PERSONAL_ACCESS_TOKEN"
   3     echo $CR_PAT | docker login ghcr.io -u YOUR_GITHUB_USERNAME --password-stdin

   2. Image korrekt benennen (taggen):
      Ein Image muss einen Namen haben, der auf die Ziel-Registry verweist. Das Format ist
  ghcr.io/OWNER/IMAGE_NAME:TAG.