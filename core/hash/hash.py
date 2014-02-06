"""
" @author VaL
" @copyright Copyright (C) 2013 VaL::bOK
" @license GNU GPL v2
"""

"""
" Base class to produce hashes of an image
"""
class Hash( object ):

    """
    " @var Image
    """
    _img = False

    """
    " @var int
    """
    _value = False

    """
    " @param Image
    """
    def __init__( self, img ):
        self._img = img
        self._value = self._calculate()

    """
    " Must be implemented in children
    "
    " @return int
    """
    def _calculate( self ):
        return 0

    """
    " @return int
    """
    @property
    def value( self ):
        return self._value

    """
    " @return Image
    """
    @property
    def img( self ):
        return self._img

    """
    " @return string
    """
    def __str__( self ):
        return str( abs( self._value ) )

    """
    " @param int
    " @param int
    " @return int
    """
    @staticmethod
    def hammingDistance( hash1, hash2 ):
        return bin( abs( hash1 ) ^ abs( hash2 ) ).count( "1" )

    """
    " @param Hash
    " @return int
    """
    def distanceTo( self, h ):
        return Hash.hammingDistance( self._value, h._value )

    """
    " @param Hash
    " @return int
    """
    def percentsTo( self, h ):
        return ( ( 64 - self.distanceTo( h ) )  * 100.0 ) / 64.0

    """
    " @return {}
    """
    def dict( self ):
        p = self.img.parent()
        px = str( p["x"] ) if p else 0
        py = str( p["y"] ) if p else 0
        return {"x": px, "y": py, "width": self.img.width, "height": self.img.height}
