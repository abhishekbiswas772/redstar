import math
from core_datastructures.sorted_set import SortedSet
from core_datastructures.dynamic_array import DArray


class GeoPoint:
    """Represents a geographical point with longitude and latitude"""
    
    def __init__(self, longitude, latitude, member):
        if not (-180 <= longitude <= 180):
            raise ValueError("Longitude must be between -180 and 180")
        if not (-85.05112878 <= latitude <= 85.05112878):
            raise ValueError("Latitude must be between -85.05112878 and 85.05112878")
        
        self.longitude = longitude
        self.latitude = latitude
        self.member = member
    
    def __str__(self):
        return f"GeoPoint({self.longitude}, {self.latitude}, {self.member})"


class Geospatial:
    """
    Redis-compatible geospatial index using Geohash and sorted set
    Stores geographical points and enables spatial queries
    """
    
    # Earth radius in meters (used for distance calculations)
    EARTH_RADIUS_M = 6372797.560856
    
    # Geohash constants
    GEOHASH_LAT_RANGE = [-90.0, 90.0]
    GEOHASH_LON_RANGE = [-180.0, 180.0]
    GEOHASH_PRECISION = 52  # bits
    
    def __init__(self):
        # Use sorted set to store geohash scores and members
        self.sorted_set = SortedSet()
        # Member to coordinates mapping
        self.coordinates = {}
    
    def _geohash_encode(self, longitude, latitude):
        """
        Encode longitude/latitude to geohash integer
        Uses interleaved bit encoding for spatial locality
        """
        lat_range = list(self.GEOHASH_LAT_RANGE)
        lon_range = list(self.GEOHASH_LON_RANGE)
        
        is_even = True
        bit = 0
        geohash = 0
        
        while bit < self.GEOHASH_PRECISION:
            if is_even:  # longitude
                mid = (lon_range[0] + lon_range[1]) / 2
                if longitude >= mid:
                    geohash = (geohash << 1) | 1
                    lon_range[0] = mid
                else:
                    geohash = geohash << 1
                    lon_range[1] = mid
            else:  # latitude
                mid = (lat_range[0] + lat_range[1]) / 2
                if latitude >= mid:
                    geohash = (geohash << 1) | 1
                    lat_range[0] = mid
                else:
                    geohash = geohash << 1
                    lat_range[1] = mid
            
            is_even = not is_even
            bit += 1
        
        return geohash
    
    def _geohash_decode(self, geohash):
        """Decode geohash integer back to longitude/latitude"""
        lat_range = list(self.GEOHASH_LAT_RANGE)
        lon_range = list(self.GEOHASH_LON_RANGE)
        
        is_even = True
        bit = self.GEOHASH_PRECISION - 1
        
        while bit >= 0:
            if is_even:  # longitude
                mid = (lon_range[0] + lon_range[1]) / 2
                if (geohash >> bit) & 1:
                    lon_range[0] = mid
                else:
                    lon_range[1] = mid
            else:  # latitude
                mid = (lat_range[0] + lat_range[1]) / 2
                if (geohash >> bit) & 1:
                    lat_range[0] = mid
                else:
                    lat_range[1] = mid
            
            is_even = not is_even
            bit -= 1
        
        longitude = (lon_range[0] + lon_range[1]) / 2
        latitude = (lat_range[0] + lat_range[1]) / 2
        
        return longitude, latitude
    
    def add(self, longitude, latitude, member):
        """Add a geographical point"""
        if not (-180 <= longitude <= 180):
            raise ValueError("Longitude must be between -180 and 180")
        if not (-85.05112878 <= latitude <= 85.05112878):
            raise ValueError("Latitude must be between -85.05112878 and 85.05112878")
        
        # Encode coordinates to geohash
        geohash = self._geohash_encode(longitude, latitude)
        
        # Store in sorted set with geohash as score
        was_new = self.sorted_set.add(member, geohash)
        
        # Store coordinates for fast lookup
        self.coordinates[member] = (longitude, latitude)
        
        return was_new
    
    def remove(self, member):
        """Remove a geographical point"""
        if member in self.coordinates:
            del self.coordinates[member]
            return self.sorted_set.remove(member)
        return False
    
    def get_position(self, member):
        """Get longitude/latitude of member"""
        if member in self.coordinates:
            return self.coordinates[member]
        return None
    
    def get_geohash(self, member):
        """Get geohash of member"""
        return self.sorted_set.get_score(member)
    
    def distance(self, member1, member2, unit='m'):
        """
        Calculate distance between two members
        Units: m (meters), km (kilometers), mi (miles), ft (feet)
        """
        pos1 = self.get_position(member1)
        pos2 = self.get_position(member2)
        
        if not pos1 or not pos2:
            return None
        
        distance_m = self._haversine_distance(pos1[1], pos1[0], pos2[1], pos2[0])
        
        # Convert to requested unit
        if unit == 'm':
            return distance_m
        elif unit == 'km':
            return distance_m / 1000.0
        elif unit == 'mi':
            return distance_m / 1609.344
        elif unit == 'ft':
            return distance_m * 3.28084
        else:
            raise ValueError("Unit must be one of: m, km, mi, ft")
    
    def _haversine_distance(self, lat1, lon1, lat2, lon2):
        """Calculate distance using Haversine formula"""
        # Convert to radians
        lat1_r = math.radians(lat1)
        lon1_r = math.radians(lon1)
        lat2_r = math.radians(lat2)
        lon2_r = math.radians(lon2)
        
        # Haversine formula
        dlat = lat2_r - lat1_r
        dlon = lon2_r - lon1_r
        
        a = math.sin(dlat/2)**2 + math.cos(lat1_r) * math.cos(lat2_r) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return self.EARTH_RADIUS_M * c
    
    def radius(self, longitude, latitude, radius, unit='m', count=None, sort_order='ASC'):
        """
        Find members within radius of given coordinates
        Returns list of members sorted by distance
        """
        if not (-180 <= longitude <= 180):
            raise ValueError("Longitude must be between -180 and 180")
        if not (-85.05112878 <= latitude <= 85.05112878):
            raise ValueError("Latitude must be between -85.05112878 and 85.05112878")
        
        # Convert radius to meters
        radius_m = radius
        if unit == 'km':
            radius_m = radius * 1000.0
        elif unit == 'mi':
            radius_m = radius * 1609.344
        elif unit == 'ft':
            radius_m = radius / 3.28084
        
        results = DArray()
        
        # Get all members and check distance
        for member in self.coordinates:
            member_pos = self.coordinates[member]
            distance_m = self._haversine_distance(latitude, longitude, member_pos[1], member_pos[0])
            
            if distance_m <= radius_m:
                # Convert back to requested unit
                if unit == 'm':
                    distance_in_unit = distance_m
                elif unit == 'km':
                    distance_in_unit = distance_m / 1000.0
                elif unit == 'mi':
                    distance_in_unit = distance_m / 1609.344
                elif unit == 'ft':
                    distance_in_unit = distance_m * 3.28084
                
                results.append((member, distance_in_unit))
        
        # Sort by distance
        results_list = []
        for i in range(len(results)):
            results_list.append(results[i])
        
        if sort_order.upper() == 'ASC':
            results_list.sort(key=lambda x: x[1])
        else:
            results_list.sort(key=lambda x: x[1], reverse=True)
        
        # Apply count limit
        if count is not None:
            results_list = results_list[:count]
        
        # Return just member names
        final_results = DArray()
        for member, distance in results_list:
            final_results.append(member)
        
        return final_results
    
    def radius_with_dist(self, longitude, latitude, radius, unit='m', count=None, sort_order='ASC'):
        """Like radius() but returns members with their distances"""
        if not (-180 <= longitude <= 180):
            raise ValueError("Longitude must be between -180 and 180")
        if not (-85.05112878 <= latitude <= 85.05112878):
            raise ValueError("Latitude must be between -85.05112878 and 85.05112878")
        
        # Convert radius to meters
        radius_m = radius
        if unit == 'km':
            radius_m = radius * 1000.0
        elif unit == 'mi':
            radius_m = radius * 1609.344
        elif unit == 'ft':
            radius_m = radius / 3.28084
        
        results = DArray()
        
        # Get all members and check distance
        for member in self.coordinates:
            member_pos = self.coordinates[member]
            distance_m = self._haversine_distance(latitude, longitude, member_pos[1], member_pos[0])
            
            if distance_m <= radius_m:
                # Convert back to requested unit
                if unit == 'm':
                    distance_in_unit = distance_m
                elif unit == 'km':
                    distance_in_unit = distance_m / 1000.0
                elif unit == 'mi':
                    distance_in_unit = distance_m / 1609.344
                elif unit == 'ft':
                    distance_in_unit = distance_m * 3.28084
                
                results.append((member, distance_in_unit))
        
        # Sort by distance
        results_list = []
        for i in range(len(results)):
            results_list.append(results[i])
        
        if sort_order.upper() == 'ASC':
            results_list.sort(key=lambda x: x[1])
        else:
            results_list.sort(key=lambda x: x[1], reverse=True)
        
        # Apply count limit
        if count is not None:
            results_list = results_list[:count]
        
        # Return alternating member/distance
        final_results = DArray()
        for member, distance in results_list:
            final_results.append(member)
            final_results.append(str(distance))
        
        return final_results
    
    def radius_by_member(self, member, radius, unit='m', count=None, sort_order='ASC'):
        """Find members within radius of given member"""
        pos = self.get_position(member)
        if not pos:
            return DArray()
        
        return self.radius(pos[0], pos[1], radius, unit, count, sort_order)
    
    def __len__(self):
        return len(self.coordinates)
    
    def size(self):
        return len(self.coordinates)