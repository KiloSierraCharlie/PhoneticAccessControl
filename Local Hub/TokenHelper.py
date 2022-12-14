from requests import Timeout, ConnectionError, post
from os import path
from json import loads, dumps
from time import sleep
from datetime import datetime
class TokenHelper:
    def __init__( self, tenant, locallyStoredDevices ):
        self.locallyStoredDevices = locallyStoredDevices
        self.lastLoadWeb = False
        self.tenant = tenant

    def retrieveToken( self, device, uid ):
        try:
            print( "[TOKEN] Attempting to load from web." )
            return self.loadTokenFromWeb( device, uid )
        except (Timeout, ConnectionError) as error:
            print( "[TOKEN] " + (("Request timed out.", "Connection error - check connection is available.")[isinstance( error, Timeout )]) )
            print( "[TOKEN] Attempting to load from local cache." )
            return self.loadTokenFromFile( device, uid )

    def loadTokenFromFile( self, device, uid ):
        self.lastLoadWeb = False
        if( device in self.locallyStoredDevices ):
            if( path.isfile( "cached/" + device + ".json" ) ):
                file = open( "cached/" + device + ".json", "r" )
                allowedUIDs = loads( file.read() )
                if( uid in allowedUIDs ):
                    print( "[CACHE] UID found in cache." )
                    return True
            else:
                print( f"[CACHE] Does not exist for {device}." )
        else:
            print( f"[CACHE] Cache is not configured for {device}." )
        return False

    def uploadOfflineLog( self ):
        while True:
            for device in self.locallyStoredDevices:
                if( path.isfile( "offline_log/" + device + ".json" ) ):
                    file = open( "offline_log/" + device + ".json", "r" )
                    log = loads( file.read() )
                    print( f"[OFFLINE LOG] Uploading {len(log)} log item(s)..." )
                    for i, logItem in enumerate(log):
                        req = post( "https://" + self.tenant + ".phoneticapps.co.uk/accesscontrol/updateLog", data=logItem )
                        print( f"[OFFLINE LOG] Attempting to upload {i+1}/{len(log)}..." )
                        if( req.status_code == 200 ):
                            log.pop( i )
                            file = open( "offline_log/" + device + ".json", "w" )
                            file.write( dumps( log ) )
                            file.close()
                            print( f"[OFFLINE LOG] Uploaded {i+1}/{len(log)}..." )
                        else:
                            print( f"[OFFLINE LOG] Upload failed, returned HTTP {req.status_code}.")
            sleep( 30 )

    def addToOfflineLog( self, device, uid ):
        logEntry = { "device": device, "uid": uid, "timestamp": str(datetime.now()) }

        if( path.isfile( "offline_log/" + device + ".json" ) ):
            file = open( "offline_log/" + device + ".json", "r" )
            log = loads( file.read() )
            log.append( logEntry )

            file = open( "offline_log/" + device + ".json", "w" )
            file.write( dumps( log ) )
            file.close()
        else:
            file = open( "offline_log/" + device + ".json", "w" )
            file.write( dumps( [logEntry] ) )
            file.close()

    def loadTokenFromWeb( self, device, uid ):
        req = post( "https://" + self.tenant + ".phoneticapps.co.uk/accesscontrol/validateUID", data={'uid': uid, 'device': device}, timeout=0.5 )
        if( req.status_code == 200 ):
            self.lastLoadWeb = True
            print( f"[TOKEN] Successfully able to validate UID: returned HTTP {req.status_code}." )
            return True
        else:
            self.lastLoadWeb = True
            print( f"[TOKEN] Unsuccessfully UID validation: returned HTTP {req.status_code}." )
        return False

    def storeTokenResult( self, device, uid, result ):
        if( path.isfile( "cached/" + device + ".json" ) ):
            curFile = open( "cached/" + device + ".json", "r" )
            curJSON = loads( curFile.read() )
            if( uid in curJSON ):
                if( not result ):
                    print( "[CACHE] Revoked UID - removing." )
                    curJSON.remove( uid )
                    file = open( "cached/" + device + ".json", "w" )
                    file.write( dumps( curJSON ) )
                    file.close()
            else:
                if( result ):
                    print( "[CACHE] New UID - inserting." )
                    curJSON.append( uid )
                    file = open( "cached/" + device + ".json", "w" )
                    file.write( dumps( curJSON ) )
                    file.close()
        else:
            if( result ):
                print( "[CACHE] New UID - inserting." )
                file = open( "cached/" + device + ".json", "w" )
                file.write( dumps( [uid] ) )
                file.close()