from __future__ import print_function

import math
import sys
from datetime import datetime, date, time, timezone
from astral import LocationInfo, sun, moon

LATITUDE = 51.505272
LONGITUDE = -0.159548
TIMEZONE = "Europe/London"
TOWN = "London"

FILENAME = '/etc/openhab/html/shaddow.svg'

WIDTH = HEIGHT = 100
PRIMARY_COLOR = '#1b3024'
LIGHT_COLOR = '#26bf75'
BG_COLOR = '#1a1919'
SUN_COLOR = '#ffff7d'
SUN_RADIUS = 5
MOON_COLOR = '#e1e1e1'
MOON_RADIUS = 3
WIND_COLOR = '#52b4bf'
STROKE_WIDTH = '1'
HOURS = 1

# Shapes of the house and garage in a 100 by 100 units square
SHAPE = [
		{ 'x': 50.1762, 'y': 4.7407 }, \
		{ 'x': 71.4071, 'y': 14.7919 }, \
		{ 'x': 53.1918, 'y': 53.2679 }, \
		{ 'x': 31.9608, 'y': 43.2167 }
	]

SHAPE_2 = []

## not really needed to edit anything below
class shadow( object ) :
	"""
	Shadow Object
	"""
	def __init__( self ) :

		self.city = LocationInfo( 'HOME', TOWN, TIMEZONE, LATITUDE, LONGITUDE )
		today = date.today()

		sun_azimuth = sun.azimuth( self.city.observer )
		print( 'Sun azimuth: ' + str( sun_azimuth ) )
		self.sun_elevation = sun.elevation( self.city.observer )
		print( 'Sun elevation: ' + str( self.sun_elevation ) )
		sunrise = sun.sunrise( self.city.observer, today )
		sunset = sun.sunset( self.city.observer, today )
		self.sunrise_azimuth = sun.azimuth( self.city.observer, sunrise )
		self.sunset_azimuth = sun.azimuth( self.city.observer, sunset )

		self.angles = self.makeListOfAngleOfHours()

		moon_azimuth = moon.azimuth( self.city.observer )
		print( 'Moon azimuth: ' + str( moon_azimuth ) )
		self.moon_elevation = moon.elevation( self.city.observer )
		print( 'Moon elevation: ' + str( self.moon_elevation ) )
		self.moon_phase = moon.phase( today )

		realSun_pos = self.degreesToPoint( sun_azimuth, 10000 )
		realMoon_pos = self.degreesToPoint( moon_azimuth, 10000 )

		self.sun_pos = self.degreesToPoint( sun_azimuth, WIDTH / 2 )
		self.moon_pos = self.degreesToPoint( moon_azimuth, WIDTH / 2 )

		if ( self.sun_elevation > 0 ) :
			self.elevation = self.sun_elevation
			self.azimuth = sun_azimuth
			self.angle_pos = self.sun_pos
			self.real_pos = realSun_pos
		else :
			self.elevation = self.moon_elevation
			self.azimuth = moon_azimuth
			self.angle_pos = self.moon_pos
			self.real_pos = realMoon_pos

	#
	#
	#
	def makeListOfAngleOfHours( self ) :
		listOfAngleOfHours = []

		for i in range( 0, 24, HOURS ) :
			timeOfHourUTC = datetime.combine( date.today(), time( i ) ).astimezone( timezone.utc )
			angleOfHour = sun.azimuth( self.city.observer, timeOfHourUTC )

			if ( angleOfHour == None ) :
				angleOfHour = 0

			listOfAngleOfHours.extend( [ angleOfHour ] )

		return listOfAngleOfHours

	#
	#
	#
	def decdeg2dms( self, dd ) :

		negative = dd < 0
		dd = abs( dd )
		minutes, seconds = divmod( dd * 3600, 60 )
		degrees, minutes = divmod( minutes, 60 )

		if negative :

			if degrees > 0 :
				degrees = -degrees
			elif minutes > 0 :
				minutes = -minutes
			else:
				seconds = -seconds

		return ( degrees, minutes, seconds )

	#
	#
	#
	def generatePath( self, stroke, fill, points, attrs = None, width = None ) :

		swith = STROKE_WIDTH
		if ( width != None ) :
			swith = width

		svg = '<path stroke="' + stroke + '" stroke-width="' + swith + '" fill="' + fill + '" '

		if ( attrs != None ) :
			svg = svg + ' ' + attrs + ' '

		svg = svg + ' d="'

		for point in points :

			if ( points.index( point ) == 0 ) :
				svg = svg + 'M' + str( point['x'] ) + ' ' + str( point['y'] )
			else :
				svg = svg + ' L' + str( point['x'] ) + ' ' + str( point['y'] )

		svg = svg + '" />'

		return svg

	#
	#
	#
	def generateArc (self, dist, stroke, fill, orig_start, orig_end, attrs = None ) :

		if ( LATITUDE < 0 ) :
			start = orig_end
			end = orig_start
		else :
			start = orig_start
			end = orig_end

		try :
			angle = end-start

			if ( angle < 0 ) :
				angle = 360 + angle

			svg = '<path d="M' + str( self.degreesToPoint( start,dist )['x'] ) + ' ' + str( self.degreesToPoint( start,dist)['y'] ) + ' '
			svg = svg + 'A' + str( dist ) + ' ' + str( dist ) + ' 0 '

			if ( angle < 180 ) :
				svg = svg + '0 1 '
			else :
				svg = svg + '1 1 '

			svg = svg + str( self.degreesToPoint( end, dist )['x'] ) + ' ' + str( self.degreesToPoint( end, dist )['y'] ) + '"'
			svg = svg + ' stroke="' + stroke + '"'

			if ( fill != None ) :
				svg = svg + ' fill="' + fill + '" '
			else :
				svg = svg + ' fill="none" '

			if ( attrs != None ) :
				svg = svg + ' ' + attrs + ' '
			else :
				svg = svg + ' stroke-width="' + STROKE_WIDTH + '"'

			svg = svg + ' />'

		except :
			svg = ''

		return svg

	#
	#
	#
	def degreesToPoint( self, d, r ) :

		coordinates = {'x': 0, 'y': 0}
		cx = WIDTH / 2
		cy = HEIGHT / 2
		d2 = 180 - d
		coordinates['x'] = cx + math.sin( math.radians( d2 ) ) * r
		coordinates['y'] = cy + math.cos( math.radians( d2 ) ) * r

		return coordinates

	#
	#
	#
	def calculateMinAndMaxPointsOfHouse ( self, shape ) :

		minPoint = -1
		maxPoint = -1
		minAngle = 999
		maxAngle = -999

		if self.debug :
			print( "" )
			print( "House:" )

		i = 0

		for point in shape :
			#Angle of distant light source (e.g. self.sun_pos)
			angle = -math.degrees( math.atan2( point['y'] - self.real_pos['y'], point['x'] - self.real_pos['x'] ) )
			distance = math.sqrt( math.pow( self.angle_pos['y'] - point['y'], 2 ) + math.pow( self.angle_pos['x'] - point['x'], 2 ) )

			if ( angle < minAngle ) :
				minAngle = angle
				minPoint = i

			if ( angle > maxAngle ) :
				maxAngle = angle
				maxPoint = i

			if self.debug :
				print( str( i ).ljust( 10 ), ":", str( point['x'] ).ljust( 10 ), str( point['y'] ).ljust( 10 ), "angle: ", str( round( angle, 7 ) ).ljust( 10 ), "dist: ", str( round( distance ) ).ljust( 10 ) )

			i = i + 1

		if self.debug :
			print( "" )
			print( "Min Point = ", minPoint )
			print( "Max Point = ", maxPoint )
			print( "" )

		return { 'minPoint': minPoint, 'maxPoint': maxPoint }

	#
	#
	#
	def findShapeBrightSide( self, shape, minPoint, maxPoint ) :

		i = minPoint
		k = 0
		sideDone = False
		side = []

		while ( not sideDone ) :

			if ( i == maxPoint ) :
				sideDone = True

			side.append( shape[i] )

			i = i + 1

			if ( i > len( shape ) - 1 ) :
				i = 0

			k = k + 1

			if ( k > len( shape ) - 1 ) : break

		return side

	#
	#
	#
	def findShapeDarkSide( self, shape, minPoint, maxPoint ) :

		i = maxPoint
		k = 0
		sideDone = False
		side = []

		while ( not sideDone ) :

			if ( i == minPoint ) :
				sideDone = True

			side.append( shape[i] )

			i = i + 1

			if ( i > len( shape ) - 1 ) :
				i = 0

			k = k + 1

			if ( k > len( shape ) - 1 ) : break

		return side

	#
	#
	#

	def drawSunnyWalls( self, shape ) :

		calculateValues = self.calculateMinAndMaxPointsOfHouse( shape )
		minPoint = calculateValues[ 'minPoint' ]
		maxPoint = calculateValues[ 'maxPoint' ]

		shapeBrightSide = self.findShapeBrightSide( shape, minPoint, maxPoint )
		shapeDarkSide = self.findShapeDarkSide( shape, minPoint, maxPoint )

		if ( self.elevation > 0 ) :
			svg = self.generatePath( LIGHT_COLOR, 'none', shapeBrightSide )
		else:
			svg = self.generatePath( PRIMARY_COLOR, 'none', shapeDarkSide )

		return svg

	#
	#
	#
	def drawShadow (self, shape ) :

		calculateValues = self.calculateMinAndMaxPointsOfHouse( shape )
		minPoint = calculateValues[ 'minPoint' ]
		maxPoint = calculateValues[ 'maxPoint' ]

		shapeDarkSide = self.findShapeDarkSide( shape, minPoint, maxPoint )

		minPointShadowX = shape[minPoint]['x'] + WIDTH * math.cos( math.radians( -self.azimuth + 270 ) )
		minPointShadowY = shape[minPoint]['y'] - WIDTH * math.sin( math.radians( -self.azimuth + 270 ) )
		maxPointShadowX = shape[maxPoint]['x'] + WIDTH * math.cos( math.radians( -self.azimuth + 270 ) )
		maxPointShadowY = shape[maxPoint]['y'] - WIDTH * math.sin( math.radians( -self.azimuth + 270 ) )

		if self.debug :
			print( "Oposite angle to sun_azimuth = ", -self.azimuth + 270 )

		shadow = [ {'x': maxPointShadowX, 'y': maxPointShadowY } ] + \
				shapeDarkSide + \
				[ {'x': minPointShadowX, 'y': minPointShadowY } ]

		svg = self.generatePath( 'none', 'black', shadow, 'mask="url(#shadowMask)" fill-opacity="0.5"' )

		return svg

	#
	#
	#
	def drawHouseFill( self, shape ) :

		svg = self.generatePath( 'none', PRIMARY_COLOR, shape )

		return svg

	#
	#
	#
	def drawBackground( self ) :

		svg = '<circle cx="' + str( WIDTH / 2 ) + '" cy="' + str( HEIGHT / 2 ) + '" r="' + str( WIDTH / 2 - 1 ) + '" fill="' + BG_COLOR + '"/>'

		return svg

	#
	#
	#
	def drawMask ( self ) :

		svg = '<defs><mask id="shadowMask">'
		svg = svg + '	  <rect width="100%" height="100%" fill="black"/>'
		svg = svg + '	  <circle cx="' + str( WIDTH / 2 ) + '" cy="' + str( HEIGHT / 2 ) + '" r="' + str( WIDTH / 2 - 1 ) + '" fill="white"/>'
		svg = svg + '</mask></defs>'

		return svg

	#
	#
	#
	def drawHourWheel( self ) :

		svg = ""

		for i in range( 0, len( self.angles ) ) :

			if ( i == len( self.angles ) - 1 ) :
				j = 0
			else :
				j = i + 1

			if ( i % 2 == 0 ) :
				svg = svg + self.generateArc( WIDTH / 2 + 8, PRIMARY_COLOR, 'none', self.angles[i], self.angles[j], 'stroke-width="3" stroke-opacity="0.2"' )
			else :
				svg = svg + self.generateArc( WIDTH / 2 + 8, PRIMARY_COLOR, 'none', self.angles[i], self.angles[j], 'stroke-width="3"' )

			if self.debug :
				print( self.angles[i] )

		svg = svg + self.generatePath( LIGHT_COLOR, 'none', [self.degreesToPoint( self.angles[0], WIDTH // 2 + 5 ), self.degreesToPoint( self.angles[0], WIDTH // 2 + 11 ) ] )
		svg = svg + self.generatePath( LIGHT_COLOR, 'none', [self.degreesToPoint( self.angles[ ( len(self.angles ) ) // 2 ], WIDTH // 2 + 5), self.degreesToPoint( self.angles[ ( len( self.angles ) ) // 2 ], WIDTH // 2 + 11 ) ] )

		return svg

	#
	#
	#
	def drawSunPath( self ) :

		svg = self.generateArc( WIDTH / 2, PRIMARY_COLOR, 'none', self.sunset_azimuth, self.sunrise_azimuth )
		svg = svg + self.generateArc( WIDTH / 2, LIGHT_COLOR, 'none', self.sunrise_azimuth, self.sunset_azimuth )

		svg = svg + self.generatePath( LIGHT_COLOR, 'none', [self.degreesToPoint( self.sunrise_azimuth, WIDTH // 2 - 2 ), self.degreesToPoint( self.sunrise_azimuth, WIDTH // 2 + 2 ) ] )
		svg = svg + self.generatePath( LIGHT_COLOR, 'none', [self.degreesToPoint( self.sunset_azimuth, WIDTH // 2 - 2 ), self.degreesToPoint( self.sunset_azimuth, WIDTH // 2 + 2 ) ] )

		return svg

	#
	#
	#
	def drawSun( self ) :

		svg = '<circle cx="' + str( self.sun_pos['x'] ) + '" cy="' + str( self.sun_pos['y'] ) + '" r="' + str( SUN_RADIUS ) + '" stroke="none" stroke-width="0" fill="' + SUN_COLOR + '55" />'
		svg = svg + '<circle cx="' + str( self.sun_pos['x'] ) + '" cy="' + str( self.sun_pos['y'] ) + '" r="' + str( SUN_RADIUS - 1 ) + '" stroke="none" stroke-width="0" fill="' + SUN_COLOR + '99" />'
		svg = svg + '<circle cx="' + str( self.sun_pos['x'] ) + '" cy="' + str( self.sun_pos['y'] ) + '" r="' + str( SUN_RADIUS - 2 ) + '" stroke="' + SUN_COLOR + '" stroke-width="0" fill="' + SUN_COLOR + '" />'

		return svg

	#
	#
	#
	def drawMoon( self ) :

		if self.debug :
			print( 'phase: ' + str( self.moon_phase ) )

		left_radius = MOON_RADIUS
		left_sweep = 0
		right_radius = MOON_RADIUS
		right_sweep = 0

		if ( self.moon_phase > 14 ) :
			right_radius = MOON_RADIUS - ( 2.0 * MOON_RADIUS * ( 1.0 - ( ( self.moon_phase % 14 ) * 0.99 / 14.0 ) ) )

			if ( right_radius < 0 ) :
				right_radius = -right_radius
				right_sweep = 0
			else :
				right_sweep = 1

		if ( self.moon_phase < 14 ) :
			left_radius = MOON_RADIUS - ( 2.0 * MOON_RADIUS * ( 1.0 - ( ( self.moon_phase % 14 ) * 0.99 / 14.0 ) ) )

			if ( left_radius < 0 ) :
				left_radius = -left_radius
				left_sweep = 1

		svg = '<path stroke="none" stroke-width="0" fill="' + MOON_COLOR \
		+ '" d="M ' + str( self.moon_pos['x'] ) + ' ' + str( self.moon_pos['y'] - MOON_RADIUS ) \
		+ ' A ' + str( left_radius ) + ' ' + str( MOON_RADIUS ) + ' 0 0 ' + str( left_sweep ) + ' ' + str( self.moon_pos['x'] ) + ' ' + str( self.moon_pos['y'] + MOON_RADIUS ) \
		+ '   ' + str( right_radius ) + ' ' + str( MOON_RADIUS ) + ' 0 0 ' + str( right_sweep ) + ' ' + str( self.moon_pos['x'] ) + ' ' + str( self.moon_pos['y'] - MOON_RADIUS ) + ' z" />'

		return svg

	#
	#
	#
	def drawWindDirection( self ) :

		svg = self.generatePath( WIND_COLOR, 'none', [ self.degreesToPoint( self.wind_angle, WIDTH // 2 + 5 ), self.degreesToPoint( self.wind_angle, WIDTH // 2 + 20 ) ], "", "2" )
		svg = svg + self.generatePath( WIND_COLOR, 'none', [ self.degreesToPoint( self.wind_angle + 5, WIDTH // 2 + 12 ), self.degreesToPoint( self.wind_angle, WIDTH // 2 + 4.2 ), self.degreesToPoint( self.wind_angle - 5, WIDTH // 2 + 12 ) ], "", "1" )

		return svg

	#
	#
	#
	def generateSVG( self ) :

		# start SVG
		svg = '<?xml version="1.0" encoding="utf-8"?>'
		svg = svg + '<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">'
		svg = svg + '<svg version="1.1" id="Layer_1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px" viewBox="-20 -20 140 140" xml:space="preserve">'

		# background
		svg = svg + self.drawBackground()

		# mask
		svg = svg + self.drawMask()

		# house shadow
		if ( self.elevation > 0 ) :
			svg = svg + self.drawShadow( SHAPE )

		# garage shadow
		if ( len( SHAPE_2 ) > 1 ) :

			if ( self.elevation > 0 ) :
				svg = svg + self.drawShadow( SHAPE_2 )

		# house fill
		svg = svg + self.drawHouseFill( SHAPE )

		# house sunny walls
		svg = svg + self.drawSunnyWalls( SHAPE )

		# GARAGE
		if ( len( SHAPE_2 ) > 1 ) :

			# garage fill
			svg = svg + self.drawHouseFill( SHAPE_2 )

			# garage sunny walls
			svg = svg + self.drawSunnyWalls( SHAPE_2 )

		# hour circle
		svg = svg + self.drawHourWheel()

		# sun path
		svg = svg + self.drawSunPath()

		# moon
		if ( self.moon_elevation > 0 ) :
			svg = svg + self.drawMoon()

		# sun
		if ( self.sun_elevation > 0 ) :
			svg = svg + self.drawSun()

		# wind
		if self.wind :
			svg = svg + self.drawWindDirection()

		# end SVG
		svg = svg + '</svg>'

		if self.debug :
			print(svg)

		f = open( FILENAME, 'w' )
		f.write( svg )
		f.close()


def main() :

	t1 = datetime.now()

	s = shadow()
	args = sys.argv

	if ( len( args ) == 1 ) :
		print('\033[91mNo parameters specified\033[0;0m')
	else :
		s.debug = update = s.wind = False

		for arg in args :

			if ( arg == "debug" ) :
				s.debug = True
			elif ( arg == "update" ) :
				update = True
			else :

				try :
					s.wind_angle = float( arg )
					s.wind = True
				except :
					s.wind = False

		if update :
			s.generateSVG()

	t2 = datetime.now()
	print( "Done in " + str( t2 - t1 ) + " seconds" )

if __name__ == '__main__' :
	main()
