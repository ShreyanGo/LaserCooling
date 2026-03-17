import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, FancyArrowPatch
from matplotlib.widgets import Slider, Button
from matplotlib.gridspec import GridSpec

def create_visualization():
    # Initial parameters
    focal_length_init = 36  # mm
    object_distance_init = 6 # inches
    sensor_distance_init = 50  # mm - initial sensor-to-lens distance
    
    # Setup fixed parameters
    sensor_width = 640  # pixels
    sensor_height = 512  # pixels
    pixel_pitch = 12  # micrometers
    mirror_diameter = 1  # inch

    tiling_plot_size = 6 # mm
    
    # Create the main figure with GridSpec layout
    fig = plt.figure(figsize=(16, 9))
    gs = GridSpec(1, 2, width_ratios=[1, 1], figure=fig)
    ax_rays = fig.add_subplot(gs[0])  # Left subplot for ray diagram
    ax_mirror = fig.add_subplot(gs[1])  # Right subplot for mirror tiling
    
    # Adjust the main plots' position to make room for sliders at the bottom
    # Increased bottom margin to accommodate three sliders
    plt.subplots_adjust(left=0.05, bottom=0.25, right=0.95, top=0.95, wspace=0.15)
    
    # Function to draw the ray optics diagram
    def draw_ray_diagram(ax, focal_length, object_distance, sensor_distance):
        ax.clear()
        
        # Convert to consistent units (mm)
        mirror_diameter_mm = mirror_diameter * 25.4  # 1 inch = 25.4 mm
        object_distance_mm = object_distance * 25.4  # inches to mm
        
        try:
            # Use the provided sensor distance instead of calculating from lens equation
            image_distance = sensor_distance
            
            # Calculate magnification: m = -i/o
            magnification = -image_distance / object_distance_mm
            
            # Calculate sensor dimensions in mm
            sensor_width_mm = sensor_width * pixel_pitch / 1000  # mm
            sensor_height_mm = sensor_height * pixel_pitch / 1000  # mm
            
            # Calculate mirror image size
            mirror_image_height_mm = abs(magnification) * mirror_diameter_mm
            
            # Define positions
            lens_pos = 0
            mirror_pos = -object_distance_mm
            sensor_pos = image_distance
            
            # Define heights (for visualization purposes)
            mirror_height = mirror_diameter_mm / 2
            mirror_image_height = mirror_image_height_mm / 2
            
            # Calculate the maximum extent of the plot
            x_min = min(mirror_pos - mirror_height, -object_distance_mm * 1.1)
            x_max = max(sensor_pos + sensor_height_mm / 2, image_distance * 1.1)
            y_max = max(mirror_height, mirror_image_height) * 1.5
            y_min = -y_max
            
            # Draw the optical axis
            ax.axhline(y=0, color='black', linestyle='-', alpha=0.3)
            
            # Draw the lens
            lens_height = y_max * 0.8
            ax.plot([lens_pos, lens_pos], [-lens_height, lens_height], 'b-', linewidth=2, label='Lens')
            
            # Draw the mirror
            ax.plot([mirror_pos, mirror_pos], [-mirror_height, mirror_height], 'g-', linewidth=2, label='Mirror')
            
            # Draw the sensor
            sensor_thickness = sensor_width_mm * 0.1
            ax.add_patch(Rectangle((sensor_pos, -sensor_height_mm/2), sensor_thickness, sensor_height_mm, 
                                 fill=True, color='gray', alpha=0.5, label='Sensor'))
            
            # Draw rays from mirror to lens to sensor
            # Ray 1: From top of mirror through center of lens
            ax.arrow(mirror_pos, mirror_height, lens_pos - mirror_pos, -mirror_height, 
                    head_width=0.5, head_length=1, fc='r', ec='r', alpha=0.6)
            ax.arrow(lens_pos, 0, sensor_pos - lens_pos, mirror_image_height, 
                    head_width=0.5, head_length=1, fc='r', ec='r', alpha=0.6)
            
            # Ray 2: From bottom of mirror through center of lens
            ax.arrow(mirror_pos, -mirror_height, lens_pos - mirror_pos, mirror_height, 
                    head_width=0.5, head_length=1, fc='r', ec='r', alpha=0.6)
            ax.arrow(lens_pos, 0, sensor_pos - lens_pos, -mirror_image_height, 
                    head_width=0.5, head_length=1, fc='r', ec='r', alpha=0.6)
            
            # Ray 3: From center of mirror through top of lens
            lens_top = lens_height * 0.7
            angle = np.arctan2(lens_top, lens_pos - mirror_pos)
            ax.arrow(mirror_pos, 0, lens_pos - mirror_pos, lens_top, 
                    head_width=0.5, head_length=1, fc='r', ec='r', alpha=0.6)
            # Calculate where this ray hits the sensor
            sensor_y = lens_top * (1 - focal_length / image_distance)
            ax.arrow(lens_pos, lens_top, sensor_pos - lens_pos, sensor_y - lens_top, 
                    head_width=0.5, head_length=1, fc='r', ec='r', alpha=0.6)
            
            # Label positions
            ax.text(mirror_pos, y_max * 0.9, f"Mirror\n(1 inch)", 
                    ha='center', va='top', fontsize=9, bbox=dict(facecolor='white', alpha=0.7))
            ax.text(lens_pos, y_max * 0.9, f"Lens\n({focal_length}mm)", 
                    ha='center', va='top', fontsize=9, bbox=dict(facecolor='white', alpha=0.7))
            ax.text(sensor_pos + sensor_thickness/2, y_max * 0.9, f"Sensor\n({sensor_width}×{sensor_height} px)", 
                    ha='center', va='top', fontsize=9, bbox=dict(facecolor='white', alpha=0.7))
            
            # Add distances
            lens_to_mirror_text = f"{object_distance:.1f} inches\n({object_distance_mm:.1f} mm)"
            ax.text((mirror_pos + lens_pos)/2, y_min * 0.8, lens_to_mirror_text, 
                    ha='center', va='bottom', fontsize=9, bbox=dict(facecolor='white', alpha=0.7))
            
            lens_to_sensor_text = f"{image_distance:.1f} mm"
            ax.text((lens_pos + sensor_pos)/2, y_min * 0.8, lens_to_sensor_text, 
                    ha='center', va='bottom', fontsize=9, bbox=dict(facecolor='white', alpha=0.7))
            
            # Add magnification information
            magn_text = f"Magnification: {magnification:.4f}"
            ax.text(x_min + (x_max - x_min) * 0.05, y_max * 0.8, magn_text, 
                    ha='left', va='top', fontsize=9, bbox=dict(facecolor='white', alpha=0.7))
            
            # Set axis limits
            margin = (x_max - x_min) * 0.05
            ax.set_xlim(x_min - margin, x_max + margin)
            ax.set_ylim(y_min - margin, y_max + margin)
            
            # Set labels and title
            ax.set_xlabel('Distance along optical axis (mm)')
            ax.set_ylabel('Height (mm)')
            ax.set_title('Ray Optics Diagram')
            
            # Add grid
            ax.grid(True, linestyle='--', alpha=0.6)
            
            # Add legend
            ax.legend(loc='upper right')
            
        except ZeroDivisionError:
            error_text = f"Error: Focal length ({focal_length}mm) must not equal object distance ({object_distance_mm:.1f}mm)"
            ax.text(0.5, 0.5, error_text, transform=ax.transAxes, 
                   horizontalalignment='center', color='red', fontsize=14)
        
        return ax
    
    # Function to update the mirror tiling plot
    def draw_mirror_tiling(ax, focal_length, object_distance, sensor_distance):
        ax.clear()
        
        # Convert to consistent units (mm)
        mirror_diameter_mm = mirror_diameter * 25.4  # 1 inch = 25.4 mm
        object_distance_mm = object_distance * 25.4  # inches to mm
        
        # Calculate sensor dimensions in mm
        sensor_width_mm = sensor_width * pixel_pitch / 1000  # mm
        sensor_height_mm = sensor_height * pixel_pitch / 1000  # mm
        
        # Use the provided sensor distance instead of calculating from lens equation
        try:
            image_distance = sensor_distance
            
            # Calculate magnification: m = -i/o
            magnification = -image_distance / object_distance_mm
            
            # Calculate mirror image diameter on sensor
            mirror_image_diameter_mm = abs(magnification) * mirror_diameter_mm
            mirror_image_radius_mm = mirror_image_diameter_mm / 2
            
            # Pixel pitch in mm
            pixel_pitch_mm = pixel_pitch / 1000

            # Calculate pixel resolution on mirror
            pixel_resolution_on_mirror_um = pixel_pitch / abs(magnification) # um
            
            # The mirror center is at (0,0)
            # Calculate where the sensor should be positioned
            sensor_center_x = 0
            sensor_center_y = 0
            sensor_start_x = sensor_center_x - sensor_width_mm / 2
            sensor_start_y = sensor_center_y - sensor_height_mm / 2
            
            # Draw sensor boundary
            ax.add_patch(Rectangle((sensor_start_x, sensor_start_y), sensor_width_mm, sensor_height_mm, 
                                  fill=False, color='green', linewidth=2, label='Sensor'))
            
            # Draw mirror image (centered at origin)
            mirror = Circle((0, 0), mirror_image_radius_mm, 
                           fill=True, color='blue', alpha=0.3, label='Mirror Image')
            ax.add_patch(mirror)
            
            # Calculate laser beam radius on sensor based on magnification
            laser_radius_mm = 0.39  # mm on the mirror
            laser_radius_on_sensor_mm = abs(magnification) * laser_radius_mm
            
            laser_beam = Circle((0, 0), 3*laser_radius_on_sensor_mm, 
                               fill=True, color='yellow', alpha=0.6, label='3× Laser Beam')
            ax.add_patch(laser_beam)
            
            laser_beam = Circle((0, 0), 2*laser_radius_on_sensor_mm, 
                               fill=True, color='orange', alpha=0.6, label='2× Laser Beam')
            ax.add_patch(laser_beam)
            
            laser_beam = Circle((0, 0), laser_radius_on_sensor_mm, 
                               fill=True, color='red', alpha=0.6, label='Laser Beam')
            ax.add_patch(laser_beam)
            
            # Draw individual pixels as tiny squares with small line indicators
            # Sample pixels to avoid overcrowding the plot (draw every 20th pixel)
            pixel_sample_rate = 20
            for i in range(0, sensor_width, pixel_sample_rate):
                for j in range(0, sensor_height, pixel_sample_rate):
                    x_mm = sensor_start_x + i * pixel_pitch_mm
                    y_mm = sensor_start_y + j * pixel_pitch_mm
                    
                    # Draw pixel outline
                    pixel = Rectangle((x_mm, y_mm), pixel_pitch_mm, pixel_pitch_mm, 
                                     fill=False, edgecolor='gray', linewidth=0.5)
                    ax.add_patch(pixel)
                    
                    # Draw small line in the center of the pixel
                    line_length = pixel_pitch_mm * 0.6
                    pixel_center_x = x_mm + pixel_pitch_mm/2
                    pixel_center_y = y_mm + pixel_pitch_mm/2
                    ax.plot([pixel_center_x, pixel_center_x + line_length/2], 
                            [pixel_center_y, pixel_center_y], 
                            color='black', linewidth=0.4)
                    ax.plot([pixel_center_x, pixel_center_x], 
                            [pixel_center_y, pixel_center_y + line_length/2], 
                            color='black', linewidth=0.4)
            
            # Set axis limits to show the entire mirror and sensor
            # Determine the maximum radius needed
            max_radius = max(mirror_image_radius_mm, 
                             max(sensor_width_mm/2, sensor_height_mm/2))
            margin = max_radius * 0.2  # Add 20% margin
            
            ax.set_xlim(-max_radius - margin, max_radius + margin)
            ax.set_ylim(-max_radius - margin, max_radius + margin)
            
            # Set labels and title
            ax.set_xlabel('Width (mm)')
            ax.set_ylabel('Height (mm)')
            ax.set_title(f'1" Mirror Projection on {sensor_width}×{sensor_height} Sensor\n'
                         f'Lens: {focal_length:.1f}mm, Distance: {object_distance:.1f}", Pixel Pitch: {pixel_pitch}µm')
            
            # Add annotations with calculations
            coverage_percent = ((np.pi * (mirror_image_radius_mm**2)) / (sensor_width_mm * sensor_height_mm) * 100)
            
            textstr = '\n'.join((
                f'Sensor dimensions: {sensor_width_mm:.2f}mm × {sensor_height_mm:.2f}mm',
                f'Mirror image diameter: {mirror_image_diameter_mm:.2f}mm',
                f'Laser beam radius: 1.3mm on mirror, {laser_radius_on_sensor_mm:.2f}mm on sensor',
                f'Magnification: {magnification:.4f}',
                f'Coverage: {coverage_percent:.1f}% of sensor area',
                f'Pixel size: {pixel_pitch}µm ({pixel_pitch_mm:.3f}mm)',
                f'Pixel size on mirror: {pixel_resolution_on_mirror_um:.1f}µm'))
            
            # Place the text box in the upper left corner
            ax.text(0.02, 0.98, textstr, transform=ax.transAxes, fontsize=9,
                    verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
            
            # Add grid markers at 1mm intervals
            ax.grid(which='major', color='gray', linestyle='--', linewidth=0.5, alpha=0.5)
            major_ticks = np.arange(-np.ceil(max_radius + margin), np.ceil(max_radius + margin) + 1, 1)
            ax.set_xticks(major_ticks)
            ax.set_yticks(major_ticks)
            
            # Add origin indicator
            ax.plot(0, 0, 'k+', markersize=10)
            ax.text(0.05, 0.05, '(0,0)', fontsize=8)
            
            # Add legend
            ax.legend(loc='lower right')
            
            # Make axis scales equal for visual accuracy
            ax.set_aspect('equal')

            ax.set_xlim((-tiling_plot_size, tiling_plot_size))
            ax.set_ylim((-tiling_plot_size, tiling_plot_size))
            
            
        except ZeroDivisionError:
            error_text = f"Error: Focal length ({focal_length}mm) must not equal object distance ({object_distance_mm:.1f}mm)"
            ax.text(0.5, 0.5, error_text, transform=ax.transAxes, 
                   horizontalalignment='center', color='red', fontsize=14)
        
        return ax
    
    # Function to update both plots
    def update_plots(focal_length, object_distance, sensor_distance):
        draw_ray_diagram(ax_rays, focal_length, object_distance, sensor_distance)
        draw_mirror_tiling(ax_mirror, focal_length, object_distance, sensor_distance)
        fig.canvas.draw_idle()
    
    # Initial plots
    update_plots(focal_length_init, object_distance_init, sensor_distance_init)
    
    # Create sliders - positioned below the plots
    ax_focal_length = plt.axes([0.2, 0.1, 0.65, 0.03], facecolor='lightgoldenrodyellow')
    ax_object_distance = plt.axes([0.2, 0.05, 0.65, 0.03], facecolor='lightgoldenrodyellow')
    # Add sensor distance slider axis below the other two sliders
    ax_sensor_distance = plt.axes([0.2, 0.0, 0.65, 0.03], facecolor='lightgoldenrodyellow')
    
    s_focal_length = Slider(ax_focal_length, 'Focal Length (mm)', 10, 100, 
                          valinit=focal_length_init, valstep=1)
    s_object_distance = Slider(ax_object_distance, 'Mirror-to-Lens Distance (in)', 3, 20, 
                             valinit=object_distance_init, valstep=0.5)
    # Add sensor distance slider widget
    s_sensor_distance = Slider(ax_sensor_distance, 'Sensor-to-Lens Distance (mm)', 20, 200,
                             valinit=sensor_distance_init, valstep=1)
    
    # Create reset button
    # Adjusted vertical position to align with middle slider
    reset_ax = plt.axes([0.01, 0.05, 0.05, 0.04])
    button = Button(reset_ax, 'Reset', color='lightgoldenrodyellow', hovercolor='0.975')
    
    # Define update function for sliders
    def update(val):
        focal_length = s_focal_length.val
        object_distance = s_object_distance.val
        # Get sensor distance from the new slider
        sensor_distance = s_sensor_distance.val
        update_plots(focal_length, object_distance, sensor_distance)
    
    # Define reset function
    def reset(event):
        s_focal_length.reset()
        s_object_distance.reset()
        # Reset sensor distance slider to initial value
        s_sensor_distance.reset()
        update_plots(focal_length_init, object_distance_init, sensor_distance_init)
    
    # Connect update functions to slider and button events
    s_focal_length.on_changed(update)
    s_object_distance.on_changed(update)
    # Connect sensor distance slider to update function
    s_sensor_distance.on_changed(update)
    button.on_clicked(reset)
    
    plt.show()

if __name__ == "__main__":
    create_visualization()