import open3d as o3d
import numpy as np
from copy import deepcopy
import os

# File path to your OBJ model
model_path = r"C:\Users\saila\OneDrive\Рабочий стол\Data\uploads_files_2787791_Mercedes+Benz+GLS+580.obj"

# Convert path to use short filename (8.3 format) to avoid Unicode issues
try:
    # Try to get the short path name for Windows
    import ctypes
    from ctypes import wintypes
    
    GetShortPathName = ctypes.windll.kernel32.GetShortPathNameW
    GetShortPathName.argtypes = [wintypes.LPCWSTR, wintypes.LPWSTR, wintypes.DWORD]
    GetShortPathName.restype = wintypes.DWORD
    
    buffer = ctypes.create_unicode_buffer(260)
    GetShortPathName(model_path, buffer, 260)
    model_path = buffer.value
except:
    # Fallback: use the path as is
    pass

print("=" * 60)
print("ASSIGNMENT #5: 3D MODEL PROCESSING WITH OPEN3D")
print("=" * 60)

# ============================================================================
# STEP 1: Loading and Visualization
# ============================================================================
print("\n[STEP 1] LOADING AND VISUALIZATION")
print("-" * 60)

mesh = o3d.io.read_triangle_mesh(model_path)
mesh.compute_vertex_normals()

print(f"✓ Model loaded successfully")
print(f"  • Number of vertices: {len(mesh.vertices)}")
print(f"  • Number of triangles: {len(mesh.triangles)}")
print(f"  • Has vertex colors: {mesh.has_vertex_colors()}")
print(f"  • Has vertex normals: {mesh.has_vertex_normals()}")

# Visualize original mesh
o3d.visualization.draw_geometries([mesh], window_name="Step 1: Original Mesh")

# ============================================================================
# STEP 2: Conversion to Point Cloud
# ============================================================================
print("\n[STEP 2] CONVERSION TO POINT CLOUD")
print("-" * 60)

# Convert mesh to point cloud
pcd = o3d.geometry.PointCloud()
pcd.points = mesh.vertices
if mesh.has_vertex_colors():
    pcd.colors = mesh.vertex_colors

print(f"✓ Converted mesh to point cloud")
print(f"  • Number of vertices (points): {len(pcd.points)}")
print(f"  • Has colors: {pcd.has_colors()}")

# Visualize point cloud
o3d.visualization.draw_geometries([pcd], window_name="Step 2: Point Cloud")

# ============================================================================
# STEP 3: Surface Reconstruction from Point Cloud
# ============================================================================
print("\n[STEP 3] SURFACE RECONSTRUCTION (POISSON)")
print("-" * 60)

# Estimate normals for Poisson reconstruction
pcd.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(
    radius=0.1, max_nn=30))

# Poisson surface reconstruction
mesh_poisson, densities = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(
    pcd, depth=9)

# Create bounding box for cropping
bbox = pcd.get_axis_aligned_bounding_box()
bbox = bbox.scale(1.1, center=bbox.get_center())
mesh_reconstructed = mesh_poisson.crop(bbox)

print(f"✓ Surface reconstructed using Poisson method")
print(f"  • Number of vertices: {len(mesh_reconstructed.vertices)}")
print(f"  • Number of triangles: {len(mesh_reconstructed.triangles)}")
print(f"  • Has vertex colors: {mesh_reconstructed.has_vertex_colors()}")

# Visualize reconstructed mesh
o3d.visualization.draw_geometries([mesh_reconstructed], 
                                 window_name="Step 3: Poisson Reconstructed Mesh")

# ============================================================================
# STEP 4: Voxelization
# ============================================================================
print("\n[STEP 4] VOXELIZATION")
print("-" * 60)

voxel_size = 0.5
voxel_grid = o3d.geometry.VoxelGrid.create_from_point_cloud(pcd, voxel_size)

print(f"✓ Voxelization completed")
print(f"  • Voxel size: {voxel_size}")
print(f"  • Number of voxels: {len(voxel_grid.get_voxels())}")
print(f"  • Has colors: {voxel_grid.has_colors()}")

# Visualize voxel grid
o3d.visualization.draw_geometries([voxel_grid], window_name="Step 4: Voxel Grid")

# ============================================================================
# STEP 5: Adding a Plane
# ============================================================================
print("\n[STEP 5] ADDING A PLANE")
print("-" * 60)

# Get mesh center and dimensions
mesh_center = mesh.get_center()
vertices_array = np.asarray(mesh.vertices)
x_min, y_min, z_min = vertices_array.min(axis=0)
x_max, y_max, z_max = vertices_array.max(axis=0)

# Create a cross-section plane through the middle (Y-Z plane at center X)
plane_size = max(z_max - z_min, y_max - y_min) * 1.5
plane_mesh = o3d.geometry.TriangleMesh.create_box(width=0.5, height=plane_size, depth=plane_size)
plane_mesh.translate([mesh_center[0] - 0.25, mesh_center[1] - plane_size/2, mesh_center[2] - plane_size/2])
plane_mesh.paint_uniform_color([0.9, 0.2, 0.2])  # Red plane

# Copy original mesh for visualization
mesh_copy = deepcopy(mesh)
mesh_copy.paint_uniform_color([0.3, 0.5, 0.9])  # Blue mesh

print(f"✓ Cross-section plane created at middle")
print(f"  • Plane position: X = {mesh_center[0]:.4f}")
print(f"  • Plane dimensions: 0.5 x {plane_size:.4f} x {plane_size:.4f}")
print(f"  • Mesh center: ({mesh_center[0]:.4f}, {mesh_center[1]:.4f}, {mesh_center[2]:.4f})")

# Visualize mesh with plane
o3d.visualization.draw_geometries([mesh_copy, plane_mesh], 
                                 window_name="Step 5: Mesh with Cross-Section Plane")

# ============================================================================
# STEP 6: Surface Clipping
# ================================================================
print("\n[STEP 6] SURFACE CLIPPING")
print("-" * 60)

import open3d as o3d
import numpy as np

# Clip mesh: keep only points with X >= mesh_center[0] (right side of plane)
vertices_array = np.asarray(mesh.vertices)
triangles_array = np.asarray(mesh.triangles)

# Get indices of vertices to keep
keep_indices = np.where(vertices_array[:, 0] >= mesh_center[0])[0]
keep_indices_set = set(keep_indices)

# Create mapping from old indices to new indices
index_mapping = {old_idx: new_idx for new_idx, old_idx in enumerate(keep_indices)}

# Filter triangles: keep only those where all 3 vertices are in keep_indices
valid_triangles = []
for tri in triangles_array:
    if all(idx in keep_indices_set for idx in tri):
        # Remap triangle indices
        new_tri = [index_mapping[idx] for idx in tri]
        valid_triangles.append(new_tri)

# Create new clipped mesh
mesh_clipped = o3d.geometry.TriangleMesh()
mesh_clipped.vertices = o3d.utility.Vector3dVector(vertices_array[keep_indices])

if valid_triangles:
    mesh_clipped.triangles = o3d.utility.Vector3iVector(np.array(valid_triangles))
    mesh_clipped.compute_vertex_normals()
    mesh_clipped.paint_uniform_color([0.3, 0.8, 0.3])  # Green clipped mesh
else:
    print("⚠ Warning: No valid triangles after clipping")

print(f"✓ Surface clipping completed (X >= {mesh_center[0]:.4f})")
print(f"  • Number of remaining vertices: {len(mesh_clipped.vertices)}")
print(f"  • Number of remaining triangles: {len(mesh_clipped.triangles)}")
print(f"  • Has vertex colors: {mesh_clipped.has_vertex_colors()}")
print(f"  • Has vertex normals: {mesh_clipped.has_vertex_normals()}")

# Visualize clipped mesh without plane
o3d.visualization.draw_geometries([mesh_clipped], window_name="Step 6: Clipped Mesh (No Plane)")

# ============================================================================
# STEP 7: Color Gradient and Extremes
# ============================================================================
print("\n[STEP 7] COLOR GRADIENT AND EXTREMES")
print("-" * 60)

# Create a fresh copy for coloring
mesh_colored = deepcopy(mesh)

# Get vertex coordinates
vertices = np.asarray(mesh_colored.vertices)

# Apply gradient along Z axis
z_coords = vertices[:, 2]
z_min = z_coords.min()
z_max = z_coords.max()

# Normalize Z coordinates to [0, 1]
z_normalized = (z_coords - z_min) / (z_max - z_min)

# Create color map (blue to red gradient)
colors = np.zeros((len(vertices), 3))
colors[:, 0] = z_normalized  # Red channel increases with Z
colors[:, 2] = 1 - z_normalized  # Blue channel decreases with Z

mesh_colored.vertex_colors = o3d.utility.Vector3dVector(colors)

# Find extreme points
min_idx = np.argmin(z_coords)
max_idx = np.argmax(z_coords)

min_point = vertices[min_idx]
max_point = vertices[max_idx]

print(f"✓ Color gradient applied (Z-axis based)")
print(f"  • Gradient range: Blue (Z-min) → Red (Z-max)")
print(f"  • Z-axis range: {z_min:.4f} to {z_max:.4f}")

print(f"\n✓ Extreme points identified:")
print(f"  • Minimum Z point: ({min_point[0]:.4f}, {min_point[1]:.4f}, {min_point[2]:.4f})")
print(f"  • Maximum Z point: ({max_point[0]:.4f}, {max_point[1]:.4f}, {max_point[2]:.4f})")
print(f"  • Z range: {z_max - z_min:.4f}")

# Create spheres at extreme points
sphere_min = o3d.geometry.TriangleMesh.create_sphere(radius=2)
sphere_min.translate(min_point)
sphere_min.paint_uniform_color([0, 0, 1])  # Blue

sphere_max = o3d.geometry.TriangleMesh.create_sphere(radius=2)
sphere_max.translate(max_point)
sphere_max.paint_uniform_color([1, 0, 0])  # Red

print(f"  • Sphere at min (blue, radius=2)")
print(f"  • Sphere at max (red, radius=2)")

# Visualize colored mesh with extreme points
o3d.visualization.draw_geometries([mesh_colored, sphere_min, sphere_max], 
                                 window_name="Step 7: Color Gradient with Extremes")

print("\n" + "=" * 60)
print("✓ ALL STEPS COMPLETED SUCCESSFULLY!")
print("=" * 60)