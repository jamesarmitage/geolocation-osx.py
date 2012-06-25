#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Julien Deudon (initbrain) - 20/03/2012 15h35
# modified to english version by Dan Gleebits 20/06/2012 15h35
# modified to run on OS X by James Armitage 25/06/2012

from commands import getoutput
import sys, re, simplejson, urllib2, webbrowser
#import os

if len(sys.argv)<1:
	print "\nUsage :\n\tpython "+sys.argv[0]+" <interface wifi>\n"

#elif os.geteuid()!=0:
#	print "Error : You must be the administrator to run this program !"

#original:
#elif not getoutput("which iw"):

#modified:
#elif not getoutput("ls /System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport"

#	print "You don't have the proper WiFi program installed :\nairport - tool for configuring Apple wireless devices from Terminal.app"
#	if not "Darwin" in getoutput("uname -a").lower(): print "This script requires Mac OS X"
else:
	print "[+] Searching for WiFi access point coordinates"

#TODO: rewrite getoutput to clean up the text, rather than bash built-ins
	iwOut=getoutput("/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport scan | tr -s ' ' | cut -d' ' -f3,4 | grep -v BSSID | sed 's/-//g'")

	if "failed" in iwOut:
		print "[!] Scanning WiFi"
	else:

#original:
#		result=re.compile("BSS ([\w\d\:]+).*\n.*\n.*\n.*\n.*\n\tsignal: ([-\d]+)", re.MULTILINE).findall(iwOut)

#modified:
#		result=re.compile("(([a-fA-F0-9]{2}[:|\-]?){6})\w([-\d]+)", re.MULTILINE).findall(iwOut)
		result=re.compile("(.*) (.*)", re.MULTILINE).findall(iwOut)



		print "[+] Creating HTML request"

		loc_req={ "version":"1.1.0",
			    "request_address":False,
			    #"addresults_language":"fr",
			    "wifi_towers":[{"mac_address":x[0].replace(":","-"),"signal_strength":int(x[1])} for x in result]
			}

		print '\n'.join([l.rstrip() for l in simplejson.dumps(loc_req, sort_keys=True, indent=4*' ').splitlines()])

		print "[+] Sending the request to Google"

		data = simplejson.JSONEncoder().encode(loc_req)
		output = simplejson.loads(urllib2.urlopen('https://www.google.com/loc/json', data).read())

		print "[+] Result"
		print '\n'.join([l.rstrip() for l in simplejson.dumps(output, sort_keys=True, indent=4*' ').splitlines()])

		print "[+] Google Map"
		print "http://maps.google.com/maps?q="+str(output["location"]["latitude"])+","+str(output["location"]["longitude"])

		print "[+] Creating the webpage"
		html="""<!DOCTYPE html>
		<html>
			<head>
				<meta name="viewport" content="initial-scale=1.0, user-scalable=no" />
				<meta http-equiv="content-type" content="text/html; charset=UTF-8"/>

				<style type="text/css">
					html, body {
						height: 100%;
						margin: 0;
						padding: 0;
					}

					#map_canvas {
						height: 100%;
					}

					@media print {
						html, body {
							height: auto;
						}

						#map_canvas {
							height: 650px;
						}
					}
				</style>

				<title>Geolocation</title>
				<script type="text/javascript" src="http://maps.googleapis.com/maps/api/js?sensor=false"></script>
				<script type="text/javascript">
					function initialize() {
						var mapOptions = {
							zoom: 17,
							center: new google.maps.LatLng("""+str(output["location"]["latitude"])+", "+str(output["location"]["longitude"])+"""),
							//mapTypeId: google.maps.MapTypeId.ROADMAP
							mapTypeId: google.maps.MapTypeId.HYBRID

						};

						var map = new google.maps.Map(document.getElementById("map_canvas"), mapOptions);

						// Construct the accuracy circle.
						var accuracyOptions = {
							strokeColor: "#000000",
							strokeOpacity: 0.8,
							strokeWeight: 2,
							fillColor: "#000000",
							fillOpacity: 0.35,
							map: map,
							center: mapOptions.center,
							radius: """+str(output["location"]["accuracy"])+"""
						};
						var accuracyCircle = new google.maps.Circle(accuracyOptions);

						var contentString = '<div>'+
							'<p><b>YOU ARE HERE !</b><br>'+
							'Latitude : """+str(output["location"]["latitude"])+"""<br>'+
							'Longitude : """+str(output["location"]["longitude"])+"""<br>'+
							'Accuracy : """+str(output["location"]["accuracy"])+"""</p>'+
							'</div>';

						var infoWindow = new google.maps.InfoWindow({
							content: contentString
						});

						var marker = new google.maps.Marker({
							position: mapOptions.center,
							map: map
						});

						google.maps.event.addListener(accuracyCircle, 'click', function() {
							infoWindow.open(map,marker);
						});

						google.maps.event.addListener(marker, 'click', function() {
							infoWindow.open(map,marker);
						});
					}
				</script>
			</head>
			<body onload="initialize()">
				<div id="map_canvas"></div>
			</body>
		</html>"""

		output = open("geolocation.html",'wb')
		output.write(html)
		output.close()

		print "[+] Open your browser"
		webbrowser.open("geolocation.html")