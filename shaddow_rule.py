# Regula uruchamiajaca skrypt
# shaddow.py
# ktory rysune plik SVG z ukladem slonca i ksiezyca w odniesieniu do domu.
# Rysunek SVG jest wykorzystywany w Habpanelu

from core.rules import rule
from core.triggers import when
from core.actions import LogAction, Exec

@rule( "Uruchom skrypt shaddow", description = "Uruchomienie skryptu do tworzenia rysunku shaddow.svg z położeniem słońca i księżyca w odniesieniu do domu", tags = [ "shaddow" ] )
@when( "Item Astro_Sun_Azimuth changed" )

def runScriptToCreateSVGfile( event ) :
	resp = Exec.executeCommandLine( Duration.ofSeconds(10), "python3", "/etc/openhab/scripts/shaddow.py", "update", str( items[ "wuWindDirAngle" ].floatValue() ) )
	LogAction.logInfo( "rule:shaddowExe:runScriptToCreateSVGfile", "Updating shaddow.SVG file: {}", resp )