import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, FancyArrowPatch
from matplotlib.widgets import Slider, Button
from matplotlib.gridspec import GridSpec

def create_visualization():
    # Initial parameters
    focal_length_init = 36  # mm
    second_focal_length_init = 50  # mm for the second lens
    object_distance_init = 34  # inches (from mirror to first lens)
    lens_separation_init = 2  # inches (distance between the two lenses)
    sensor_distance_init = 100  # mm - distance from second lens to sensor
    
    # Setup fixed parameters
    sensor_width = 640 # pixels
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
    # Increased bottom margin for five sliders
    plt.subplots_adjust(left=0.05, bottom=0.30, right=0.95, top=0.95, wspace=0.15)
    
    # Function to draw the ray optics diagram
    def draw_ray_diagram(ax, focal_length1, focal_length2, object_distance, lens_separation, sensor_distance):
        ax.clear()
        
        # Convert to consistent units (mm)
        mirror_diameter_mm = mirror_diameter * 25.4  # 1 inch = 25.4 mm
        object_distance_mm = object_distance * 25.4  # inches to mm
        lens_separation_mm = lens_separation * 25.4  # inches to mm
        
        try:
            # Calculate the image distance after the first lens (intermediate image)
            # Using thin lens equation: 1/f = 1/o + 1/i
            # Solving for i: i = (o*f)/(o-f)
            intermediate_image_distance = (object_distance_mm * focal_length1) / (object_distance_mm - focal_length1)
            
            # The object distance for the second lens is the lens separation minus the intermediate image distance
            second_object_distance = lens_separation_mm - intermediate_image_distance
            
            # Use the provided sensor distance instead of calculating from lens equation
            final_image_distance = sensor_distance
            
            # Total distance from the first lens to the final image
            total_image_distance = lens_separation_mm + final_image_distance
            
            # Calculate magnification
            # Total magnification is the product of the magnifications of each lens
            # For first lens: m1 = -intermediate_image_distance / object_distance_mm
            # For second lens: m2 = -final_image_distance / second_object_distance
            magnification1 = -intermediate_image_distance / object_distance_mm
            magnification2 = -final_image_distance / second_object_distance if second_object_distance != 0 else float('inf')
            total_magnification = magnification1 * magnification2
            
            # Calculate sensor dimensions in mm
            sensor_width_mm = sensor_width * pixel_pitch / 1000  # mm
            sensor_height_mm = sensor_height * pixel_pitch / 1000  # mm
            
            # Calculate mirror image size
            mirror_image_height_mm = abs(total_magnification) * mirror_diameter_mm
            
            # Define positions
            lens1_pos = 0
            lens2_pos = lens_separation_mm
            mirror_pos = -object_distance_mm
            intermediate_image_pos = intermediate_image_distance
            sensor_pos = lens1_pos + total_image_distance
            
            # Define heights (for visualization purposes)
            mirror_height = mirror_diameter_mm / 2
            mirror_image_height = mirror_image_height_mm / 2
            
            # Calculate the maximum extent of the plot
            x_min = min(mirror_pos - mirror_height, -object_distance_mm * 1.1)
            x_max = max(sensor_pos + sensor_height_mm / 2, total_image_distance * 1.1)
            y_max = max(mirror_height, mirror_image_height) * 1.5
            y_min = -y_max
            
            # Draw the optical axis
            ax.axhline(y=0, color='black', linestyle='-', alpha=0.3)
            
            # Draw the first lens
            lens_height = y_max * 0.8
            ax.plot([lens1_pos, lens1_pos], [-lens_height, lens_height], 'b-', linewidth=2, label='Lens 1')
            
            # Draw the second lens
            ax.plot([lens2_pos, lens2_pos], [-lens_height, lens_height], 'b-', linewidth=2, alpha=0.7, label='Lens 2')
            
            # Draw the mirror
            ax.plot([mirror_pos, mirror_pos], [-mirror_height, mirror_height], 'g-', linewidth=2, label='Mirror')
            
            # Draw the sensor
            sensor_thickness = sensor_width_mm * 0.1
            ax.add_patch(Rectangle((sensor_pos, -sensor_height_mm/2), sensor_thickness, sensor_height_mm, 
                                 fill=True, color='gray', alpha=0.5, label='Sensor'))
            
            # Draw rays from mirror through both lenses to sensor
            # Calculate the height of the ray at each lens and the final image
            
            # Ray 1: From top of mirror through centers of both lenses
            ax.arrow(mirror_pos, mirror_height, lens1_pos - mirror_pos, -mirror_height, 
                    head_width=0.5, head_length=1, fc='r', ec='r', alpha=0.6)
            ax.arrow(lens1_pos, 0, lens2_pos - lens1_pos, 0, 
                    head_width=0.5, head_length=1, fc='r', ec='r', alpha=0.6)
            ax.arrow(lens2_pos, 0, sensor_pos - lens2_pos, mirror_image_height, 
                    head_width=0.5, head_length=1, fc='r', ec='r', alpha=0.6)
            
            # Ray 2: From bottom of mirror through centers of both lenses
            ax.arrow(mirror_pos, -mirror_height, lens1_pos - mirror_pos, mirror_height, 
                    head_width=0.5, head_length=1, fc='r', ec='r', alpha=0.6)
            ax.arrow(lens1_pos, 0, lens2_pos - lens1_pos, 0, 
                    head_width=0.5, head_length=1, fc='r', ec='r', alpha=0.6)
            ax.arrow(lens2_pos, 0, sensor_pos - lens2_pos, -mirror_image_height, 
                    head_width=0.5, head_length=1, fc='r', ec='r', alpha=0.6)
            
            # Ray 3: Draw a ray from the center of the mirror at an angle
            lens_top = lens_height * 0.7
            angle = np.arctan2(lens_top, lens1_pos - mirror_pos)
            ax.arrow(mirror_pos, 0, lens1_pos - mirror_pos, lens_top, 
                    head_width=0.5, head_length=1, fc='r', ec='r', alpha=0.6)
            
            # Calculate where this ray hits the second lens
            # For simplicity, use linear proportion for the height at second lens
            # This is a simplification and not physically accurate for all cases
            lens2_height = lens_top * (1 - intermediate_image_distance / (lens2_pos - lens1_pos))
            ax.arrow(lens1_pos, lens_top, lens2_pos - lens1_pos, lens2_height - lens_top, 
                    head_width=0.5, head_length=1, fc='r', ec='r', alpha=0.6)
            
            # For the final leg, calculate based on the magnification of the second lens
            sensor_y = lens2_height * (1 - focal_length2 / final_image_distance)
            ax.arrow(lens2_pos, lens2_height, sensor_pos - lens2_pos, sensor_y - lens2_height, 
                    head_width=0.5, head_length=1, fc='r', ec='r', alpha=0.6)
            
            # Optional: Draw the intermediate image position if it's between the lenses
            if 0 < intermediate_image_distance < lens_separation_mm:
                ax.axvline(x=intermediate_image_distance, color='purple', linestyle='--', alpha=0.5, label='Intermediate Image')
                
            # Label positions with reduced font size for better spacing
            ax.text(mirror_pos, y_max * 0.9, f"Mirror\n(1\")", 
                    ha='center', va='top', fontsize=8, bbox=dict(facecolor='white', alpha=0.8))
            ax.text(lens1_pos, y_max * 0.9, f"Lens 1\n({focal_length1}mm)", 
                    ha='center', va='top', fontsize=8, bbox=dict(facecolor='white', alpha=0.8))
            ax.text(lens2_pos, y_max * 0.9, f"Lens 2\n({focal_length2}mm)", 
                    ha='center', va='top', fontsize=8, bbox=dict(facecolor='white', alpha=0.8))
            ax.text(sensor_pos + sensor_thickness/2, y_max * 0.9, f"Sensor\n({sensor_width}×{sensor_height}px)", 
                    ha='center', va='top', fontsize=8, bbox=dict(facecolor='white', alpha=0.8))
            
            # Add distances with staggered vertical positions to avoid overlap
            lens_to_mirror_text = f"{object_distance:.1f}\"\n({object_distance_mm:.1f}mm)"
            ax.text((mirror_pos + lens1_pos)/2, y_min * 0.95, lens_to_mirror_text, 
                    ha='center', va='bottom', fontsize=8, bbox=dict(facecolor='white', alpha=0.8))
            
            lens_separation_text = f"{lens_separation:.1f}\"\n({lens_separation_mm:.1f}mm)"
            ax.text((lens1_pos + lens2_pos)/2, y_min * 0.75, lens_separation_text, 
                    ha='center', va='bottom', fontsize=8, bbox=dict(facecolor='white', alpha=0.8))
            
            lens_to_sensor_text = f"{final_image_distance:.1f}mm"
            ax.text((lens2_pos + sensor_pos)/2, y_min * 0.95, lens_to_sensor_text, 
                    ha='center', va='bottom', fontsize=8, bbox=dict(facecolor='white', alpha=0.8))
            
            # Add magnification information
            magn_text = f"Total Magnification: {total_magnification:.4f}"
            ax.text(x_min + (x_max - x_min) * 0.05, y_max * 0.8, magn_text, 
                    ha='left', va='top', fontsize=9, bbox=dict(facecolor='white', alpha=0.7))
            
            # Set axis limits
            margin = (x_max - x_min) * 0.05
            ax.set_xlim(x_min - margin, x_max + margin)
            ax.set_ylim(y_min - margin, y_max + margin)
            
            # Set labels and title
            ax.set_xlabel('Distance along optical axis (mm)')
            ax.set_ylabel('Height (mm)')
            ax.set_title('Ray Optics Diagram with Teleside Converter')
            
            # Add grid
            ax.grid(True, linestyle='--', alpha=0.6)
            
            # Add legend
            ax.legend(loc='upper right')
            
        except ZeroDivisionError:
            error_text = "Error: Optical configuration error. Check if focal lengths match distances."
            ax.text(0.5, 0.5, error_text, transform=ax.transAxes, 
                   horizontalalignment='center', color='red', fontsize=14)
        except Exception as e:
            error_text = f"Error: {str(e)}"
            ax.text(0.5, 0.5, error_text, transform=ax.transAxes, 
                   horizontalalignment='center', color='red', fontsize=14)
        
        return ax
    
    # Function to update the mirror tiling plot
    def draw_mirror_tiling(ax, focal_length1, focal_length2, object_distance, lens_separation, sensor_distance):
        ax.clear()
        
        # Convert to consistent units (mm)
        mirror_diameter_mm = mirror_diameter * 25.4  # 1 inch = 25.4 mm
        object_distance_mm = object_distance * 25.4  # inches to mm
        lens_separation_mm = lens_separation * 25.4  # inches to mm
        
        # Calculate sensor dimensions in mm
        sensor_width_mm = sensor_width * pixel_pitch / 1000  # mm
        sensor_height_mm = sensor_height * pixel_pitch / 1000  # mm
        
        # Calculate optical parameters for two-lens system
        try:
            # First lens calculations
            intermediate_image_distance = (object_distance_mm * focal_length1) / (object_distance_mm - focal_length1)
            magnification1 = -intermediate_image_distance / object_distance_mm
            
            # The object distance for the second lens depends on the intermediate image position
            second_object_distance = lens_separation_mm - intermediate_image_distance
            
            # Use the provided sensor distance instead of calculating from lens equation
            final_image_distance = sensor_distance
            magnification2 = -final_image_distance / second_object_distance if second_object_distance != 0 else float('inf')
            
            # Total magnification of the system
            total_magnification = magnification1 * magnification2
            
            # Calculate mirror image diameter on sensor
            mirror_image_diameter_mm = abs(total_magnification) * mirror_diameter_mm
            mirror_image_radius_mm = mirror_image_diameter_mm / 2
            
            # Pixel pitch in mm
            pixel_pitch_mm = pixel_pitch / 1000

            # Calculate pixel resolution on mirror
            pixel_resolution_on_mirror_um = pixel_pitch / abs(total_magnification) # um
            
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
            laser_radius_on_sensor_mm = abs(total_magnification) * laser_radius_mm
            
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
                         f'Teleside: L1:{focal_length1:.1f}mm, L2:{focal_length2:.1f}mm, Distance:{object_distance:.1f}"')
            
            # Add annotations with calculations - more compact formatting
            coverage_percent = ((np.pi * (mirror_image_radius_mm**2)) / (sensor_width_mm * sensor_height_mm) * 100)
            
            textstr = '\n'.join((
                f'Sensor: {sensor_width_mm:.2f}×{sensor_height_mm:.2f}mm',
                f'Mirror img: {mirror_image_diameter_mm:.2f}mm',
                f'Laser: 1.3mm→{laser_radius_on_sensor_mm:.2f}mm',
                f'Total mag: {total_magnification:.4f}',
                f'L1 mag: {magnification1:.4f}',
                f'L2 mag: {magnification2:.4f}',
                f'Coverage: {coverage_percent:.1f}%',
                f'Pixel: {pixel_pitch}µm',
                f'Pixel on mirror: {pixel_resolution_on_mirror_um:.1f}µm'))
            
            # Place the text box in the upper left corner with smaller font
            ax.text(0.02, 0.98, textstr, transform=ax.transAxes, fontsize=7.5,
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
            error_text = "Error: Optical configuration error. Check if focal lengths match distances."
            ax.text(0.5, 0.5, error_text, transform=ax.transAxes, 
                   horizontalalignment='center', color='red', fontsize=14)
        except Exception as e:
            error_text = f"Error: {str(e)}"
            ax.text(0.5, 0.5, error_text, transform=ax.transAxes, 
                   horizontalalignment='center', color='red', fontsize=14)
        
        return ax
    
    # Function to update both plots
    def update_plots(focal_length1, focal_length2, object_distance, lens_separation, sensor_distance):
        draw_ray_diagram(ax_rays, focal_length1, focal_length2, object_distance, lens_separation, sensor_distance)
        draw_mirror_tiling(ax_mirror, focal_length1, focal_length2, object_distance, lens_separation, sensor_distance)
        fig.canvas.draw_idle()
    
    # Initial plots
    update_plots(focal_length_init, second_focal_length_init, object_distance_init, lens_separation_init, sensor_distance_init)
    
    # Create sliders - positioned below the plots
    # Stack five sliders vertically from top to bottom
    ax_lens_separation = plt.axes([0.2, 0.23, 0.65, 0.03], facecolor='lightgoldenrodyellow')
    ax_focal_length1 = plt.axes([0.2, 0.18, 0.65, 0.03], facecolor='lightgoldenrodyellow')
    ax_focal_length2 = plt.axes([0.2, 0.13, 0.65, 0.03], facecolor='lightgoldenrodyellow')
    ax_object_distance = plt.axes([0.2, 0.08, 0.65, 0.03], facecolor='lightgoldenrodyellow')
    # Add sensor distance slider axis
    ax_sensor_distance = plt.axes([0.2, 0.03, 0.65, 0.03], facecolor='lightgoldenrodyellow')
    
    s_focal_length1 = Slider(ax_focal_length1, 'Lens 1 Focal Length (mm)', 10, 100, 
                          valinit=focal_length_init, valstep=1)
    s_focal_length2 = Slider(ax_focal_length2, 'Lens 2 Focal Length (mm)', 10, 100, 
                          valinit=second_focal_length_init, valstep=1)
    s_object_distance = Slider(ax_object_distance, 'Mirror-to-Lens Distance (in)', 10, 50, 
                             valinit=object_distance_init, valstep=0.5)
    s_lens_separation = Slider(ax_lens_separation, 'Lens Separation (in)', 0.5, 5, 
                             valinit=lens_separation_init, valstep=0.1)
    # Add sensor distance slider widget
    s_sensor_distance = Slider(ax_sensor_distance, 'Sensor-to-Lens2 Distance (mm)', 20, 300,
                             valinit=sensor_distance_init, valstep=1)
    
    # Create reset button
    # Adjusted vertical position to align with middle of slider stack
    reset_ax = plt.axes([0.01, 0.13, 0.05, 0.04])
    button = Button(reset_ax, 'Reset', color='lightgoldenrodyellow', hovercolor='0.975')
    
    # Define update function for sliders
    def update(val):
        focal_length1 = s_focal_length1.val
        focal_length2 = s_focal_length2.val
        object_distance = s_object_distance.val
        lens_separation = s_lens_separation.val
        # Get sensor distance from the new slider
        sensor_distance = s_sensor_distance.val
        update_plots(focal_length1, focal_length2, object_distance, lens_separation, sensor_distance)
    
    # Define reset function
    def reset(event):
        s_focal_length1.reset()
        s_focal_length2.reset()
        s_object_distance.reset()
        s_lens_separation.reset()
        # Reset sensor distance slider to initial value
        s_sensor_distance.reset()
        update_plots(focal_length_init, second_focal_length_init, object_distance_init, lens_separation_init, sensor_distance_init)
    
    # Connect update functions to slider and button events
    s_focal_length1.on_changed(update)
    s_focal_length2.on_changed(update)
    s_object_distance.on_changed(update)
    s_lens_separation.on_changed(update)
    # Connect sensor distance slider to update function
    s_sensor_distance.on_changed(update)
    button.on_clicked(reset)
    
    plt.show()

if __name__ == "__main__":
    create_visualization()