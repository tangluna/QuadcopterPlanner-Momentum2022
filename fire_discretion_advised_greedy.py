from student_base import student_base
import time
import numpy
from typing import Dict
from shapely.geometry import Point, LineString, Polygon, MultiPolygon # ADDED IMPORT
import geojson # ADDED IMPORT

class my_flight_controller(student_base):
    """
    Student flight controller class.

    Students develop their code in this class.

    Parameters
    ----------
    student_base : student_base
        Class defining functionality enabling base functionality
    
    Methods
    -------
    student_run(self, telemetry: Dict, commands: Dict (optional))
        Method that takes in telemetry and issues drone commands.
    """
    
    def refill_tank(self, telemetry):
        """
        TODO dummy water retrieving! from one location. need to locate different or closest water source?
        make go to nearest water source??
        """
        print("Get to water")
        goalLat = 42.3608 # water
        goalLon = -70.9904
        goalAlt = 100 
        self.goto(goalLat, goalLon, goalAlt)
        err = numpy.linalg.norm([goalLat - telemetry['latitude'], goalLon - telemetry['longitude']])
        tol = 0.0001 # Approximately 50 feet tolerance
        while err > tol:
            print('Aircraft is enroute to water')
            time.sleep(10)
            err = numpy.linalg.norm([goalLat - telemetry['latitude'], goalLon - telemetry['longitude']])
        print("Picking up water")
        water_start_time = time.time()
        while(time.time() - water_start_time < 60.0):
            print("Water level: " + str(round(telemetry['water_pct_remaining'], 2)) + '%')
            time.sleep(5)
        print("Water level: " + str(round(telemetry['water_pct_remaining'], 2)) + '%')
    
    def extinguish_fire(self, lat, long, alt, description, telemetry, fire):
        """
        TODO add description!
        """
        print("Navigating to: (" + str(lat) + ", " + str(long) + ")")
        self.goto(lat, long, alt)
        err = numpy.linalg.norm([lat - self.telemetry['latitude'], long - self.telemetry['longitude']])
        tol = 0.0001 # Approximately 50 feet tolerance
        while err > tol:
            print('Aircraft is enroute to ' + description)
            time.sleep(10)
            err = numpy.linalg.norm([lat - telemetry['latitude'], long - telemetry['longitude']])
        old_fire_pct = telemetry['fires_pct_remaining']
        curr_fire_pct = 0
        while old_fire_pct - curr_fire_pct > 0.01:
            old_fire_pct = self.telemetry['fires_pct_remaining']
            time.sleep(2)
            curr_fire_pct = self.telemetry['fires_pct_remaining']
            print("Waiting for fire to extinguish. Current fire pct: " + str(curr_fire_pct))
            print("Error: " + str(old_fire_pct - curr_fire_pct))
        print("Fire extinguished finished")
    
    def calculate_gain_greedy(self, fire, lat, long, telemetry):
        """
        TODO LATER CONVERT TO TIME INSTEAD OF DISTANCE, ADD IN WATER DISTANCE
        """
        gain = fire.area/fire.distance(Point(lat, long))
        print("Current water level: " + str(telemetry['water_pct_remaining']))
        print("Current fire: " + str(fire))
        print("Current gain: " + str(gain))
        return gain
    
    def student_run(self, telemetry: Dict, commands: Dict) -> None:
        """
        Defines drone behavior with respect to time given the telemetry.

        Students develop their based code in this method (you may develop)
        your own methods and classes in addition to this).

        Parameters
        ----------
        telemetry : Dict
            Telemetry coming from the simulated drone.
        commands : Dict
            Issue basic commands via this dictionary (you use the method in 
               the example missions).
        """
  
        # Student code goes in this method.
        # See student_fire_example_boston.py and 
          # student_SAR_example_boston.py for ideas on
        # how to fill out this method to complete the challenge.
        print("Arming")
        self.arm()
        
        print("Taking off")
        homeLat = telemetry['latitude']
        homeLon = telemetry['longitude']
        self.takeoff()

        # ADD UP AREAS OF ALL FIRES -- IF LESS THAN 60, DO CURRENT CODE
        total_area = 0
        for fire in telemetry['fire_polygons']:
            total_area += fire.area
        
        print("Total area: " + str(total_area))

        if total_area <= .0000056709:
            print("Fires can be extinguished with only 1 fill.")
            self.refill_tank(telemetry) # nearest water source
            prev_fire = None
            while True:
                highest_gain = -1.0
                greedy_fire = None
                for fire in telemetry['fire_polygons']:
                    if prev_fire == None or not (prev_fire != None and fire.equals(prev_fire)): #short circuit eval
                        current_gain = self.calculate_gain_greedy(fire, telemetry['latitude'], telemetry['longitude'], telemetry)
                        if current_gain > highest_gain:
                            highest_gain = current_gain
                            greedy_fire = fire
                print("Next fire: " + str(greedy_fire))
                self.extinguish_fire(greedy_fire.centroid.y, greedy_fire.centroid.x, 100, 'next fire', telemetry, greedy_fire)
                prev_fire = greedy_fire
        else:
            pass
"""            
            # only searching for things inside of map bounds??
            with open("./data/waterbodies.geojson") as f:
                gj = geojson.load(f)
            features = gj['features']
            closest_water = {}
            for fire in telemetry['fire_polygons']:
                closest_water_distance = 100000000
                closest_water_coord = Point(0,0)
                for water in features:
                    print("Current Water: " + str(water['geometry']))
                    if water['geometry']['type'] == 'LineString':
                        water_body = LineString(water['geometry']['coordinates'])
                    elif water['geometry']['type'] == 'Polygon':
                        water_body = Polygon(water['geometry']['coordinates'][0])
                    elif water['geometry']['type'] == 'MultiPolygon':
                        #water_body = MultiPolygon(water['geometry']['coordinates'])
                        pass
                    print("WATER: " + str(water_body))
                    distance = fire.distance(water_body)
                    print("Flag 1")
                    if distance < closest_water_distance:
                        closest_water_distance = distance
                    print("Flag 2")
                print("Flag 3")
                closest_water[fire] = closest_water_distance
            print("Dictionary: " + str(closest_water))
            '''
            # add in closest point
            # find closest water
            # add fire-water-coord pair to dictionary
            # IF NOT, DEAL WITH OTHER WATER
            # use different gain function
            # map out how far each fire is from water -- from geojson
            # pick a point in the center of each fire (centroid), distance from there to nearest water as well as lat and long of the water
            # store in dictionary
"""
'''
        self.refill_tank(telemetry)

        prev_fire = None
        
        while True:
            highest_gain = -1.0
            greedy_fire = None
            for fire in telemetry['fire_polygons']:
                if prev_fire == None or not (prev_fire != None and fire.equals(prev_fire)): #short circuit eval
                    current_gain = self.calculate_gain_greedy(fire, telemetry['latitude'], telemetry['longitude'], telemetry)
                    if current_gain > highest_gain:
                        highest_gain = current_gain
                        greedy_fire = fire
            
            print("Next fire: " + str(greedy_fire))

            self.navigate_to(greedy_fire.centroid.y, greedy_fire.centroid.x, 100, 'next fire', telemetry)
            prev_fire = greedy_fire

        

        while True:
            if round(telemetry['water_pct_remaining'], 2))
'''

        
    




# This bit of code just makes it so that this class actually runs when executed from the command line,
# rather than just being silently defined.

if __name__ == "__main__":
    fcs = my_flight_controller()
    fcs.run()
