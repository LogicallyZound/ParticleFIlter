#!/usr/bin/env python
import rospy
from nav_msgs.msg import OccupancyGrid, MapMetaData
from geometry_msgs.msg import Pose, PointStamped, Quaternion, Point

import numpy as np

class Map(object):
    """ The Map class represents an occupancy grid.

    This is an abstract superclass.

    Public instance variables:

        width      --  Number of columns in the occupancy grid.
        height     --  Number of rows in the occupancy grid.
        resolution --  Width of each grid square in meters.
        origin_x   --  Position of the grid cell (0,0) in
        origin_y   --    in the map coordinate system.
        grid       --  numpy array with height rows and width columns.

    Note that x increases with increasing column number and y increases
    with increasing row number.
    """

    def __init__(self, *args, **kwargs):
        """ Construct an empty occupancy grid.

        Can be called -either- with a single OccupancyGrid message as
        the argument, or with any of the following provided as named
        arguments:

           keyword arguments:
                   origin_x,
                   origin_y  -- The position of grid cell (0,0) in the
                                map coordinate frame. (default -2.5, -2.5)
                   resolution-- width and height of the grid cells
                                in meters. (default .1)
                   width,
                   height    -- The grid will have height rows and width
                                columns cells.  width is the size of
                                the x-dimension and height is the size
                                of the y-dimension. (default 50, 50)

         The default arguments put (0,0) in the center of the grid.
        """

        if len(args) == 1 and isinstance(args[0], OccupancyGrid):
            self._init_from_message(args[0])
        else:
            raise ValueError("Constructor only supports named arguments.")


    def _init_from_message(self, map_message):
        """
        Set up a map as an in-memory version of an OccupancyGrid message
        """
        self.width = map_message.info.width
        self.height = map_message.info.height
        self.resolution = map_message.info.resolution
        self.origin_x = map_message.info.origin.position.x
        self.origin_y = map_message.info.origin.position.y
        self.grid = self._data_to_numpy(map_message.data)

    def _numpy_to_data(self):
        """
        Convert the numpy array containing grid data to a python
        list suitable for use as the data field in an OccupancyGrid
        message.
        """
        flat_grid = self.grid.reshape((self.grid.size,)) * 100
        data = list(np.array(np.round(flat_grid), dtype='int8'))
        return data

    def _data_to_numpy(self, data):
        """
        Convert the integer data field in an OccupancyGrid message to
        2d real valued numpy array.
        """
        np_data = np.array(data).reshape(self.height, self.width)
        return np_data / 100.0

    def _cell_index(self, x, y):
        """
        Helper method for finding map index.  x and y are in the map
        coordinate system.
        """
        x -= self.origin_x
        y -= self.origin_y
        row = int(np.floor(y / self.resolution))
        col = int(np.floor(x / self.resolution))
        return row, col

    def to_message(self):
        """ Return a nav_msgs/OccupancyGrid representation of this map. """
        grid_msg = OccupancyGrid()
        grid_msg.header.stamp = rospy.Time.now()
        grid_msg.header.frame_id = "map"
        grid_msg.info.resolution = self.resolution
        grid_msg.info.width = self.width
        grid_msg.info.height = self.height
        grid_msg.info.origin = Pose(Point(self.origin_x, self.origin_y, 0),
                                    Quaternion(0, 0, 0, 1))
        grid_msg.data = self._numpy_to_data()
        return grid_msg

    def cell_position(self, row, col):
        """
        Determine the x, y cooridantes of the center of a particular grid cell.
        """
        x = col * self.resolution + .5 * self.resolution + self.origin_x
        y = row * self.resolution + .5 * self.resolution + self.origin_y
        return x, y

    def set_cell(self, x, y, val):
        """
        Set the value in the grid cell containing position (x,y).
        x and y are in the map coordinate system
        """
        row, col = self._cell_index(x, y)
        try:
            if row >= 0 and col >= 0:
                self.grid[row, col] = val
        except IndexError:
            pass

    def get_cell(self, x, y):
        """
        Get the value from the grid cell containing position (x,y).
        x and y are in the map coordinate system
        """
        row, col = self._cell_index(x, y)
        val = float('nan')
        try:
            if row >= 0 and col >= 0:
                val = self.grid[row, col]
        except IndexError:
            pass
        return val
