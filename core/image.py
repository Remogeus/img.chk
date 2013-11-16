"""
" @author VaL
" @copyright Copyright (C) 2013 VaL::bOK
" @license GNU GPL v2
"""
import PIL
from PIL import ImageStat
import numpy as np
import cv2
import cPickle as pickle

"""
" Base class to handle image comparisons
"""
class Image( object ):
    _keypoints = []
    _descriptors = []
    _img = False

    def __init__( self, img ):
        self._img = img

    """
    " @return Image
    """
    @staticmethod
    def get( filename ):
        return Image.read( filename ).compute()

    """
    " @return Image
    """
    @staticmethod
    def read( filename ):
        i = cv2.imread( filename, 1 )
        if i is None:
            raise Exception( "Could not read file", filename )
        i = Image( i )
        i._filename = filename
        return i

    """
    " @return self
    """
    def compute( self ):
        surf = cv2.SURF( 400 )
        self._keypoints, self._descriptors = surf.detectAndCompute( self._img, None )

        return self

    """
    " @return Image
    """
    def toGrayscale( self ):
        return Image( cv2.cvtColor( self._img, cv2.COLOR_BGR2GRAY ) )

    """
    " @return Image
    """
    def resize( self, size, inter = cv2.INTER_NEAREST ):
        return Image( cv2.resize( self._img, size, interpolation=inter ) )

    @staticmethod
    def _toArray( keypoints, descriptors ):
        result = []
        i = 0
        for point in keypoints:
            temp = ( point.pt, point.size, point.angle, point.response, point.octave, point.class_id, descriptors[i] )
            i += 1
            result.append( temp )

        return result

    @staticmethod
    def _fromArray( array ):
        keypoints = []
        descriptors = []
        for point in array:
            temp_feature = cv2.KeyPoint( x = point[0][0], y = point[0][1], _size = point[1], _angle = point[2], _response = point[3], _octave = point[4], _class_id = point[5] )
            temp_descriptor = point[6]
            keypoints.append( temp_feature )
            descriptors.append( temp_descriptor )

        return keypoints, np.array( descriptors )

    """
    " @return array
    """
    def serialize( self ):
        return Image._toArray( self._keypoints, self._descriptors )

    """
    " @return self
    " @see serialize()
    """
    def unserialize( self, array ):
        self._keypoints, self._descriptors = Image._fromArray( array )

        return self

    """
    " @return Image
    """
    def dumpToFile( self, fn ):
        pickle.dump( self.serialize(), open( fn, "wb" ) )

        return self

    """
    " @return string
    """
    def dump( self ):
        return pickle.dumps( self.serialize() )

    """
    " @return self
    """
    def loadFromFile( self, fn ):
        db = pickle.load( open( fn, "rb" ) )

        return self.unserialize( db )

    """
    " @return self
    """
    def load( self, st ):
        db = pickle.loads( st )

        return self.unserialize( db )

    """
    " @return zip
    """
    @staticmethod
    def _filterMatches( kp1, kp2, matches, ratio = 0.75 ):
        mkp1, mkp2 = [], []
        for m in matches:
            if len( m ) == 2 and m[0].distance < m[1].distance * ratio:
                m = m[0]
                mkp1.append( kp1[m.queryIdx] )
                mkp2.append( kp2[m.trainIdx] )

        pairs = zip( mkp1, mkp2 )

        return pairs

    """
    " @return (DMatch, DMatch)
    """
    def _knnMatch( self, img ):
        matcher = cv2.BFMatcher( cv2.NORM_L2 )
        kp1 = self._keypoints
        desc1 = self._descriptors
        kp2 = img._keypoints
        desc2 = img._descriptors
        matches = matcher.knnMatch( desc1, trainDescriptors = desc2, k = 2 )
        pairs = Image._filterMatches( kp1, kp2, matches )

        return pairs

    """
    " @return float
    """
    def _knnMatchInPercent( self, img ):
        pairs = self._knnMatch( img )
        l1 = len( self._keypoints )
        l2 = len( img._keypoints )
        lp = len( pairs )
        r = ( lp * 100 ) / l1

        return r

    """
    " @return bool
    """
    def knnMatched( self, img, p = 5 ):
        p12 = self._knnMatchInPercent( img )
        p21 = img._knnMatchInPercent( self )

        return p12 > p or p21 > p

    """
    " @return int
    """
    def ahash( self ):
        img = self.toGrayscale().resize( (8, 8) )
        averageValue = ImageStat.Stat( img ).mean[0]
        result = 0
        for row in xrange( 8 ):
            for col in xrange( 8 ):
                result <<= 1
                result |= 1 * ( img.getpixel( (col, row) ) >= averageValue )

        return result

    """
    " @return int
    """
    def pixel( self, x, y ):
        return self._img[x,y]

    """
    " @return int
    """
    def dhash( self ):
        img = self.toGrayscale().resize( (8, 8), cv2.INTER_AREA  )

        previous = img.pixel( 7, 7 )
        result = 0
        for row in xrange( 8 ):
            for col in xrange( 8 ):
                result <<= 1
                pixel = img.pixel( col, row )
                result |= 1 * ( pixel >= previous )
                previous = pixel

        return result

    """
    " @return int
    """
    @staticmethod
    def hammingDistance( hash1, hash2 ):
        return bin( hash1 ^ hash2 ).count( "1" )

    """
    " @return int
    """
    def phash( self ):
        img = self.toGrayscale().resize( (32, 32), cv2.INTER_NEAREST )
        imf = np.float32( img._img ) / 255.0
        dsty = cv2.dct( imf )[0:8]
        dst = []
        for i in xrange( len( dsty ) ):
            dst.append( dsty[i][0:8] )

        c = a = 0
        for j in xrange( len( dst ) ):
            y = dst[j]
            for i in xrange( len( y ) ):
                if i == 0 and j == 0:
                    continue

                c += 1
                a += y[i]

        median = a / c
        result = 0
        for row in xrange( 8 ):
            for col in xrange( 8 ):
                result <<= 1
                result |= 1 * ( dst[col][row] > median )

        return result
