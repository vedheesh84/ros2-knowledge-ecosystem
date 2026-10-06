#!/usr/bin/env python3
"""
terrain_mapper.py - Terrain Mapping for Quadruped Navigation

LEARNING OBJECTIVES:
- Understanding elevation maps
- Depth camera processing
- Terrain assessment for locomotion

TERRAIN MAPPING:
Quadrupeds need to understand terrain to:
1. Plan foot placements (avoid holes)
2. Adjust gait for slopes
3. Detect obstacles
4. Estimate traversability

This node creates a 2.5D elevation map from RGB-D camera data.
"""

import numpy as np
from typing import Optional

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import PointCloud2, Image
from nav_msgs.msg import OccupancyGrid
from std_msgs.msg import Float32MultiArray


class TerrainMapper(Node):
    """
    Creates elevation map from depth camera.

    Subscribes:
    - /camera/depth/points: Point cloud from RGB-D camera

    Publishes:
    - /terrain/elevation_map: Height grid
    - /terrain/traversability: Traversability score grid
    """

    def __init__(self):
        super().__init__('terrain_mapper')

        # Parameters
        self.declare_parameter('resolution', 0.05)  # m per cell
        self.declare_parameter('map_size', 2.0)  # m, square map
        self.declare_parameter('max_slope', 0.3)  # max traversable slope (rad)

        self.resolution = self.get_parameter('resolution').value
        self.map_size = self.get_parameter('map_size').value
        self.max_slope = self.get_parameter('max_slope').value

        # Grid dimensions
        self.grid_size = int(self.map_size / self.resolution)

        # Elevation map (2D array of heights)
        self.elevation = np.zeros((self.grid_size, self.grid_size))
        self.elevation_count = np.zeros((self.grid_size, self.grid_size))

        # ==================== SUBSCRIBERS ====================
        self.cloud_sub = self.create_subscription(
            PointCloud2, '/camera/depth/points', self.pointcloud_callback, 10)

        # ==================== PUBLISHERS ====================
        self.elevation_pub = self.create_publisher(
            Float32MultiArray, '/terrain/elevation_map', 10)
        self.traversability_pub = self.create_publisher(
            OccupancyGrid, '/terrain/traversability', 10)

        # Timer for publishing (10 Hz)
        self.create_timer(0.1, self.publish_maps)

        self.get_logger().info('Terrain Mapper initialized')

    def pointcloud_callback(self, msg: PointCloud2):
        """
        Process point cloud to update elevation map.

        For learning purposes, this uses a simplified approach.
        Production systems use libraries like grid_map or elevation_mapping.
        """
        # Simplified: In real implementation, would parse PointCloud2
        # and project points to ground-centered grid

        # For demo, generate synthetic terrain
        self.generate_demo_terrain()

    def generate_demo_terrain(self):
        """Generate demo terrain for testing without real sensor."""
        # Create flat ground with some variation
        x = np.linspace(-self.map_size/2, self.map_size/2, self.grid_size)
        y = np.linspace(-self.map_size/2, self.map_size/2, self.grid_size)
        X, Y = np.meshgrid(x, y)

        # Gentle hills
        self.elevation = 0.02 * np.sin(X * 3) * np.cos(Y * 3)

        # Add a step
        self.elevation[self.grid_size//4:self.grid_size//2, :] += 0.1

    def compute_traversability(self) -> np.ndarray:
        """
        Compute traversability from elevation map.

        Traversability considers:
        - Slope (gradient of elevation)
        - Roughness (local variance)
        - Height relative to robot

        Returns:
            2D array of traversability scores [0, 100]
            Higher = more traversable
        """
        # Compute gradient (slope)
        gy, gx = np.gradient(self.elevation, self.resolution)
        slope = np.sqrt(gx**2 + gy**2)

        # Compute roughness (local variance)
        from scipy.ndimage import uniform_filter
        mean_elev = uniform_filter(self.elevation, size=3, mode='nearest')
        roughness = uniform_filter((self.elevation - mean_elev)**2, size=3, mode='nearest')
        roughness = np.sqrt(roughness)

        # Traversability score
        # Penalize steep slopes and rough terrain
        slope_score = 100 * np.exp(-slope / self.max_slope)
        roughness_score = 100 * np.exp(-roughness / 0.05)

        traversability = 0.7 * slope_score + 0.3 * roughness_score
        return traversability.astype(np.int8)

    def publish_maps(self):
        """Publish elevation and traversability maps."""
        # Elevation map
        elev_msg = Float32MultiArray()
        elev_msg.data = self.elevation.flatten().tolist()
        self.elevation_pub.publish(elev_msg)

        # Traversability as OccupancyGrid
        traversability = self.compute_traversability()

        grid = OccupancyGrid()
        grid.header.stamp = self.get_clock().now().to_msg()
        grid.header.frame_id = 'base_link'
        grid.info.resolution = self.resolution
        grid.info.width = self.grid_size
        grid.info.height = self.grid_size
        grid.info.origin.position.x = -self.map_size / 2
        grid.info.origin.position.y = -self.map_size / 2
        grid.data = (100 - traversability).flatten().tolist()  # Invert for occupancy

        self.traversability_pub.publish(grid)


def main(args=None):
    rclpy.init(args=args)
    node = TerrainMapper()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
