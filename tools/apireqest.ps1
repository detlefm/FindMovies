<#
.SYNOPSIS
    Ruft einen WebService auf, prüft den Statuscode, wandelt die XML-Antwort in ein Hashtable um und gibt sie als JSON aus.
.DESCRIPTION
    Dieses Skript sendet eine GET-Anfrage an einen WebService, prüft den HTTP-Statuscode,
    konvertiert die XML-Antwort in ein PowerShell-Hashtable und gibt sie formatiert als JSON aus.
.PARAMETER Uri
    Die URL des WebServices, der aufgerufen werden soll.
.PARAMETER PrettyPrint
    Wenn gesetzt, wird der JSON-String mit Einrückungen formatiert (Standard: $true).
.EXAMPLE
    .\Invoke-WebServiceToJson.ps1 -Uri "https://example.com/api/data"
.EXAMPLE
    .\Invoke-WebServiceToJson.ps1 -Uri "https://example.com/api/data" -PrettyPrint $false
#>

param (
    [Parameter(Mandatory=$true)]
    [string]$Uri,
    
    [Parameter(Mandatory=$false)]
    [bool]$PrettyPrint = $true
)

try {
    # WebService aufrufen
    Write-Host "Rufe WebService auf: $Uri"
    $response = Invoke-WebRequest -Uri $Uri -Method Get
    
    # Statuscode prüfen
    if ($response.StatusCode -ne 200) {
        throw "WebService antwortete mit Statuscode $($response.StatusCode)"
    }
    
    Write-Host "Erfolgreiche Antwort vom WebService (Status $($response.StatusCode))"
    
    # XML aus der Antwort extrahieren
    [xml]$xmlResponse = $response.Content
    
    # Funktion zum Konvertieren von XML in ein Hashtable
    function Convert-XmlToHashtable {
        param (
            [System.Xml.XmlNode]$node
        )
        
        $hashtable = @{}
        
        # Attribute hinzufügen
        if ($node.Attributes) {
            foreach ($attr in $node.Attributes) {
                $hashtable[$attr.Name] = $attr.Value
            }
        }
        
        # Child-Elemente verarbeiten
        foreach ($child in $node.ChildNodes) {
            if ($child.HasChildNodes -or $child.Attributes.Count -gt 0) {
                # Wenn das Kind weitere Kinder oder Attribute hat, rekursiv verarbeiten
                $hashtable[$child.Name] = Convert-XmlToHashtable -node $child
            } else {
                # Einfache Werte direkt hinzufügen
                $hashtable[$child.Name] = $child.InnerText
            }
        }
        
        return $hashtable
    }
    
    # XML in Hashtable umwandeln
    $resultHashtable = Convert-XmlToHashtable -node $xmlResponse
    
    # Hashtable in JSON konvertieren
    $jsonOutput = $resultHashtable | ConvertTo-Json -Depth 10 -Compress:(!$PrettyPrint)
    
    # JSON-Ergebnis ausgeben
    # Write-Host "`nJSON Ausgabe:`n"
    # $jsonOutput
    
    # JSON-String für weitere Verarbeitung zurückgeben
    return $jsonOutput
}
catch {
    Write-Host "Fehler beim Aufruf des WebServices: $_" -ForegroundColor Red
    exit 1
}