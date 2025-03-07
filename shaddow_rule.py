from core.rules import rule
from core.triggers import when
from core.actions import LogAction, Exec

@rule( "Run script shaddow", description = "Run script to create SVG drawing with sun and moon positions in relation to the house", tags = [ "shaddow" ] )
@when( "Item Sun_Azimuth changed" )
@when( "Item Wind_Angle changed" )

def runScriptToCreateSVGfile( event ) :
	resp = Exec.executeCommandLine( Duration.ofSeconds(10), "python3", "/etc/openhab/scripts/shaddow.py", "update", str( items[ "Wind_Angle" ].floatValue() ) )
	LogAction.logInfo( "rule:runScriptToCreateSVGfile", "Updating shaddow.SVG file: {}", resp )
